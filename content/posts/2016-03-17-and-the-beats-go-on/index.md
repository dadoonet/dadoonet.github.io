---
title: "And the beats go on!"
description: "Creating a new beat: soundbeat"
author: David Pilato
avatar: /about/david_pilato.png
tags:
  - beats
  - elasticsearch
  - kibana
  - go
categories:
  - tutorial
date: 2016-03-17 17:35:39 +0100
nolastmod: true
cover: featured.png
draft: false
aliases:
  - /blog/2016/03/17/and-the-beats-go-on/
  - /blog/2016-03-17-and-the-beats-go-on/
---

Sounds like a cool music, right? At least this is one of my favorite tracks.

{{< youtube fOaxEa5ONJw >}}

May be some of you already know that, I enjoy doing [some DeeJaying](https://itunes.apple.com/fr/podcast/dj-dadoo.net-mixes/id959495351)
for my friends.

But today, I want to speak about another kind of beats. Elastic beats!

{{< figure src="beats.png" caption="Elastic Beats" >}}

<!--more-->

Actually my favorite funky music track is a one from Georges Duke: Reach out!
But this is another story...

{{< youtube Aw0MpVVNj0g >}}

## Beats

So what are beats?

> Beats are lightweight shippers that collect and ship all kinds of operational data to Elasticsearch

Important terms here:

* `lightweight`: indeed, written in Golang, using few resources
* `all kinds of operational data`: yeah! You are just limited by your imagination 😊. It can come from a [network card](https://www.elastic.co/products/beats/packetbeat) from where you can *sniff* a known protocol such as MySQL, PostgreSQL, MongoDB, ICMP, HTTP... It can come from a [file](https://www.elastic.co/products/beats/filebeat) you can basically `tail -f` to elasticsearch. It can come from various [metrics](https://www.elastic.co/products/beats/topbeat) from your system, like running a TOP command on every single machine you have and correlate information from them...

So very flexible...

I came with this idea... I like music. I like beats. Let's try to create another beat: `soundbeat`!

## Prerequisites

You need to have:

* `go`: `brew install go`
* `glide`: `brew install glide`

## Soundbeat

The goal is more to learn how to write a beat than the feature itself.
The `soundbeat` will read a MP3 file, then extract the sound level for left and right channels using a given period for each sample.

The final goal is to generate a waveform like this:

{{< figure src="TheWhispers-AndTheBeatGoesOn.png" caption="And the beat goes on" >}}

### Generate a beat from a template

We will use the great Beat generator project which basically creates a skeleton for your beat.

```sh
cookiecutter beat-generator
```

The generator is asking some questions:

```txt
project_name [Examplebeat]: soundbeat
github_name [your-github-name]: dadoonet
beat [soundbeat]: 
beat_path [github.com/dadoonet]: 
full_name [Firstname Lastname]: David Pilato
```

Just `cd` in the generated dir:

```sh
cd $GOPATH/src/github.com/dadoonet/soundbeat
```

You have a full beat project:

```sh
$ tree
.
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── beater
│   └── soundbeat.go
├── config
│   └── config.go
├── dev-tools
│   └── packer
│       ├── Makefile
│       ├── beats
│       │   └── soundbeat.yml
│       └── version.yml
├── docs
│   └── index.asciidoc
├── etc
│   ├── beat.yml
│   ├── fields.yml
│   └── soundbeat.template.json
├── glide.yaml
├── main.go
├── main_test.go
└── tests
    └── system
        ├── config
        │   └── soundbeat.yml.j2
        ├── requirements.txt
        ├── soundbeat.py
        └── test_base.py
```

This project depends on [libbeat](https://github.com/elastic/beats/tree/master/libbeat) which provides already all the needed stuff to read configuration file or write data to stdout or elasticsearch.

Just run now:

```sh
make
```

It will install the needed dependencies and create your git repository and `git add` all your files.

If you run `make` again, it will compile and build your binary `soundbeat`.

### libsox sound library

The [SoX library](https://sourceforge.net/projects/sox/) provides all the tool we need for our use case.
You have different ways for installing the library. On my mac, I used:

```sh
brew install sox
```

Kristoffer Grönlund created a [golang binding for SoX](https://github.com/krig/go-sox). Let's use it.

In `glide.yaml`, we add this dependency:

```yaml
- package: github.com/krig/go-sox
```

Then pull the library from internet with:

```sh
make update-deps
```

We now have the library. We can start coding our beat.

### Writing the logic

All the code will basically go into `beater/soundbeat.go`.

#### Import libs

We have to import all the needed libs:

```go
import (
 "fmt"
 "time"
 "errors"
 "math"

 "github.com/krig/go-sox"

 "github.com/elastic/beats/libbeat/beat"
 "github.com/elastic/beats/libbeat/cfgfile"
 "github.com/elastic/beats/libbeat/common"
 "github.com/elastic/beats/libbeat/logp"

 "github.com/dadoonet/soundbeat/config"
)
```

#### Soundbeat settings

We will define 3 settings:

* `name`: MP3 filename
* `period`: size of one sound sample (like `100ms`)
* `zoom`: it's basically a hack for a better rendering in Kibana as it [does not support aggregations under 1 second](https://github.com/elastic/kibana/issues/6559).

```go
type Soundbeat struct {
 beatConfig *config.Config
 done       chan struct{}

 name       string
 period     time.Duration
 zoom       float64
}
```

Settings are read from `soundbeat.yml` file by default. This file is automatically generated from the default libbeat configuration file and the content of `etc/beat.yml`.

We can change this file and provide a default example:

```yaml
################### Soundbeat Configuration Example #########################

############################# Soundbeat ######################################

soundbeat:
  # MP3 file to analyze
  name: musics/TheWhispers-AndTheBeatGoesOn.mp3
  # Defines the size of each sample
  period: 100ms
  # Zoom factor for a better Kibana rendering (default to 1.0)
  zoom: 10.0
```

The `config/config.go` file managed this configuration file:

```go
// Config is put into a different package to prevent cyclic imports in case
// it is needed in several locations

package config

type Config struct {
 Soundbeat SoundbeatConfig
}

type SoundbeatConfig struct {
 Name string `yaml:"name"`
 Period string `yaml:"period"`
 Zoom float64 `yaml:"zoom"`
}
```

We need to change the code in `Setup` method:

```go
func (bt *Soundbeat) Setup(b *beat.Beat) error {
  // All libSoX applications must start by initializing the SoX library
 if !sox.Init() {
  return errors.New("Failed to initialize SoX")
 }
  // Make sure to call Quit before terminating
  defer sox.Quit()

  period, err := configDuration(bt.beatConfig.Soundbeat.Period, 10 * time.Millisecond)
  if err != nil {
    return err
  }

 name := bt.beatConfig.Soundbeat.Name
 if name == "" {
  return errors.New("no name set")
 }

  zoom := 1.0
  if bt.beatConfig.Soundbeat.Zoom != 0.0 {
    zoom = bt.beatConfig.Soundbeat.Zoom
  }

  bt.name = name
  bt.period = period
  bt.zoom = zoom

  return nil
}

func configDuration(cfg string, d time.Duration) (time.Duration, error) {
  if cfg != "" {
    return time.ParseDuration(cfg)
  } else {
    return d, nil
  }
}
```

In this method, we make sure that `libSoX` is working well. We also define all default values and check that a name has been set.

### The Run method

The `Run` method is where we need to implement the logic. It will read the file, extract the samples and for each sample will generate an event which should be sent to elasticsearch.

This opens the file for reading:

```go
in := sox.OpenRead(bt.name)
if in == nil {
  logp.Err("Failed to open input file")
}
// Close the file before exiting
defer in.Release()
```

The total duration is the number of samples given by `Length()` divided by 2 (as we expect a stereo file) divided by the rate give by `Rate()`.

For example, for the MP3 file of `The Whispers`, we have `26 123 340` samples, the file is a stereo file (2 tracks) and the bitrate is `44 100 Hz`.
So the duration of the track is: `26123340/2/44100` which is `296.182s`

```go
duration := float64(in.Signal().Length()) / float64(in.Signal().Channels()) / in.Signal().Rate()
```

We will use the `@timestamp` defacto standard for the timestamp field in Logstash/Beats/Kibana applications.
So we will start from `now()` and add a new sample every `period`.

We also apply the zoom factor to the time scale.

```go
modifed_period := float64(period.Nanoseconds()) * bt.zoom
now = now.Add(time.Duration(modifed_period))
```

For each sample, we get the level of the sound for left and right channels and we store them in `left` and `right` fields.

Then we generate an event which contains this information and we publish it:

```go
event := common.MapStr{
  "@timestamp":   common.Time(now),
  "type":         b.Name,
  "left":         left * 100.0,
  "right":        right * 100.0,
}

b.Events.PublishEvent(event)
```

This is how the full `Run` method looks like:

```go
func (bt *Soundbeat) Run(b *beat.Beat) error {
  logp.Info("soundbeat is starting...")

  // Open the input file (with default parameters)
  in := sox.OpenRead(bt.name)
  if in == nil {
    logp.Err("Failed to open input file")
  }
  // Close the file before exiting
  defer in.Release()

  // This example program requires that the audio has precisely 2 channels:
  if in.Signal().Channels() != 2 {
    logp.Err("Input must be 2 channels")
  }

  duration := float64(in.Signal().Length()) / float64(in.Signal().Channels()) / in.Signal().Rate()

  now := time.Now()

  period := bt.period

  // Convert block size (in seconds) to a number of samples:
  block_size := int64(period.Seconds() * float64(in.Signal().Rate()) * float64(in.Signal().Channels()) + 0.5)
  // Make sure that this is at a `wide sample' boundary:
  block_size -= block_size % int64(in.Signal().Channels())
  // Allocate a block of memory to store the block of audio samples:
  buf := make([]sox.Sample, block_size)

  // Read and process blocks of audio for the selected duration or until EOF:
  for blocks := 0; in.Read(buf, uint(block_size)) == block_size && float64(blocks) * period.Seconds() < duration; blocks++ {
    left := 0.0
    right := 0.0

    // We increment time with a block_size (in seconds)
    // But we first zoom accordingly to the zoom factor we set
    modifed_period := float64(period.Nanoseconds()) * bt.zoom
    now = now.Add(time.Duration(modifed_period))

    for i := int64(0); i < block_size; i++ {
      // convert the sample from SoX's internal format to a `float64' for
      // processing in this application:
      sample := sox.SampleToFloat64(buf[i])

      // The samples for each channel are interleaved; in this example
      // we allow only stereo audio, so the left channel audio can be found in
      // even-numbered samples, and the right channel audio in odd-numbered
      // samples:
      if (i & 1) != 0 {
        right = math.Max(right, math.Abs(sample))
      } else {
        left = math.Max(left, math.Abs(sample))
      }
    }

    event := common.MapStr{
      "@timestamp":   common.Time(now),
      "type":         b.Name,
      "left":         left * 100.0,
      "right":        right * 100.0,
    }

    b.Events.PublishEvent(event)
  }

  logp.Info("soundbeat ended analyzing file %s", bt.name)
  return nil
}
```

We can now build our beat:

```sh
# This will merge our changes in etc/beat.yml to ./soundbeat.yml
make update
# This will compile
make
```

And use it! This will start our beat in debug mode without pushing anything:

```sh
./soundbeat -N -e -d "*"
```

It will produce something like:

```txt
2016/03/18 12:40:18.031084 beat.go:221: DBG  Initializing output plugins
2016/03/18 12:40:18.031128 publish.go:205: INFO Dry run mode. All output types except the file based one are disabled.
2016/03/18 12:40:18.031144 geolite.go:24: INFO GeoIP disabled: No paths were set under shipper.geoip.paths
2016/03/18 12:40:18.031186 publish.go:291: INFO Publisher name: MacBook-Pro-4.local
2016/03/18 12:40:18.031320 beat.go:238: INFO Init Beat: soundbeat; Version: 5.0.0-SNAPSHOT
2016/03/18 12:40:18.031670 soundbeat.go:76: INFO soundbeat has been configured:
2016/03/18 12:40:18.031681 soundbeat.go:77: INFO  - Name: musics/TheWhispers-AndTheBeatGoesOn.mp3
2016/03/18 12:40:18.031687 soundbeat.go:78: INFO  - Period: 100ms
2016/03/18 12:40:18.031703 soundbeat.go:79: INFO  - Zoom: 10.000000
2016/03/18 12:40:18.031769 beat.go:267: INFO soundbeat sucessfully setup. Start running.
2016/03/18 12:40:18.031774 soundbeat.go:93: INFO soundbeat is starting...
2016/03/18 12:40:18.032152 soundbeat.go:116: INFO  - Duration 296.182993 s
2016/03/18 12:40:18.032165 soundbeat.go:117: INFO  - Channels 2
2016/03/18 12:40:18.032171 soundbeat.go:118: INFO  - Rate 44100 Hz
2016/03/18 12:40:18.032721 publish.go:112: DBG  Publish: {
  "@timestamp": "2016-03-18T12:40:19.032Z",
  "beat": {
    "hostname": "MacBook-Pro-4.local",
    "name": "MacBook-Pro-4.local"
  },
  "left": 0,
  "right": 0,
  "type": "soundbeat"
}
...
2016/03/18 12:38:52.469365 async.go:48: DBG  publisher disabled
2016/03/18 12:38:52.469688 publish.go:112: DBG  Publish: {
  "@timestamp": "2016-03-18T13:28:10.947Z",
  "beat": {
    "hostname": "MacBook-Pro-4.local",
    "name": "MacBook-Pro-4.local"
  },
  "left": 0,
  "right": 0,
  "type": "soundbeat"
}
2016/03/18 12:38:52.469695 async.go:48: DBG  publisher disabled
2016/03/18 12:38:52.469768 soundbeat.go:167: INFO soundbeat ended analyzing file musics/TheWhispers-AndTheBeatGoesOn.mp3
2016/03/18 12:38:52.469911 beat.go:307: INFO Start exiting beat
2016/03/18 12:38:52.469926 beat.go:282: INFO Stopping Beat
2016/03/18 12:38:52.469937 beat.go:290: INFO Cleaning up soundbeat before shutting down.
2016/03/18 12:38:52.469945 beat.go:139: INFO Exit beat completed
```

## Connecting to elasticsearch

We need to define a template for elasticsearch if we want to force elasticsearch using our mapping.
But we are lucky! The beat-generator provides everything out of the box!

Just edit `etc/fields.yml` and change the `soundbeat` part to:

```yaml
soundbeat:
  type: group
  fields:
    - name: name
      type: string
      required: true
      description: >
        Sound file name
    - name: left
      type: double
      required: true
      description: >
        Left sound level
    - name: right
      type: double
      required: true
      description: >
        Right sound level
```

Then, run:

```sh
make update
```

It will generate the `etc/soundbeat.template.json` file. And cherry on the cake, it will also update the documentation in `docs` dir.

Start elasticsearch:

```sh
bin/elasticsearch
[2016-03-18 14:53:33,487][INFO ][node                     ] [Katu] version[2.2.1], pid[82105], build[d045fc2/2016-03-09T09:38:54Z]
[2016-03-18 14:53:33,489][INFO ][node                     ] [Katu] initializing ...
[2016-03-18 14:53:34,111][INFO ][plugins                  ] [Katu] modules [lang-expression, lang-groovy], plugins [], sites []
[2016-03-18 14:53:34,285][INFO ][env                      ] [Katu] using [1] data paths, mounts [[/ (/dev/disk1)]], net usable_space [3.6gb], net total_space [464.7gb], spins? [unknown], types [hfs]
[2016-03-18 14:53:34,285][INFO ][env                      ] [Katu] heap size [990.7mb], compressed ordinary object pointers [true]
[2016-03-18 14:53:34,286][WARN ][env                      ] [Katu] max file descriptors [10240] for elasticsearch process likely too low, consider increasing to at least [65536]
[2016-03-18 14:53:36,456][INFO ][node                     ] [Katu] initialized
[2016-03-18 14:53:36,456][INFO ][node                     ] [Katu] starting ...
[2016-03-18 14:53:36,572][INFO ][transport                ] [Katu] publish_address {127.0.0.1:9300}, bound_addresses {[fe80::1]:9300}, {[::1]:9300}, {127.0.0.1:9300}
[2016-03-18 14:53:36,584][INFO ][discovery                ] [Katu] elasticsearch/b_T6HUb-TXyUTN8Af6YdEQ
[2016-03-18 14:53:39,618][INFO ][cluster.service          ] [Katu] new_master {Katu}{b_T6HUb-TXyUTN8Af6YdEQ}{127.0.0.1}{127.0.0.1:9300}, reason: zen-disco-join(elected_as_master, [0] joins received)
[2016-03-18 14:53:39,638][INFO ][http                     ] [Katu] publish_address {127.0.0.1:9200}, bound_addresses {[fe80::1]:9200}, {[::1]:9200}, {127.0.0.1:9200}
[2016-03-18 14:53:39,638][INFO ][node                     ] [Katu] started
```

And apply the template:

```sh
curl -XPUT 'http://localhost:9200/_template/soundbeat' -d@etc/soundbeat.template.json
```

And launch `soundbeat` again with the standard mode:

```sh
./soundbeat
```

In elasticsearch logs, you should see:

```sh
[2016-03-18 14:54:31,599][INFO ][cluster.metadata         ] [Katu] [soundbeat-2016.03.18] creating index, cause [auto(bulk api)], templates [soundbeat], shards [5]/[1], mappings [_default_, soundbeat]
[2016-03-18 14:54:31,725][INFO ][cluster.metadata         ] [Katu] [soundbeat-2016.03.18] update_mapping [soundbeat]
[2016-03-18 14:54:31,744][INFO ][cluster.routing.allocation] [Katu] Cluster health status changed from [RED] to [YELLOW] (reason: [shards started [[soundbeat-2016.03.18][4], [soundbeat-2016.03.18][4]] ...]).
```

## Visualize in Kibana

Just launch Kibana:

```sh
bin/kibana
```

And open <http://0.0.0.0:5601/>

You have to change the time range. And look into the future!

Why this? Because we injected data from now and generated a 5 minutes long music waveform.
But remember that we used a `zoom` factor of `10x` for a better rendering in Kibana.

So here, I'll look at data from `2016-03-18 14:54:30` to `2016-03-18 15:03:30` for the begining of the music.

{{< figure src="kibana1.png" caption="Select time range" >}}

Let's create a Timeseries visualization!

{{< figure src="kibana2.png" caption="Timeseries visualization" >}}

Then, we define interval to `1s` and set the Timelion expression:

```js
.es(index="soundbeat-*",metric="min:left").bars(1)
```

{{< figure src="kibana3.png" caption="Left waveform" >}}

We can also add the right channel:

```js
.es(index="soundbeat-*",metric="min:left").bars(1),.es(index="soundbeat-*",metric="min:right").bars(1)
```

{{< figure src="kibana4.png" caption="With Right waveform" >}}

But this will overlap. So let's fix that by negative by `1` the left channel:

```js
.es(index="soundbeat-*",metric="min:left").multiply(-1).bars(1),.es(index="soundbeat-*",metric="min:right").bars(1)
```

We now have something which looks like the waveform we are looking for!

{{< figure src="kibana5.png" caption="Final waveform" >}}

## Resources

* [Beats Platform Reference](https://www.elastic.co/guide/en/beats/libbeat/current/index.html)
* [Beat Generator](https://github.com/elastic/beat-generator)
* Beat developer guide
* [soundbeat source code](https://github.com/dadoonet/soundbeat)
