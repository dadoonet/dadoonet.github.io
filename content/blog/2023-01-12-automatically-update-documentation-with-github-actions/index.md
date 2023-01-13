---
title: "Automatically update documentation with Github Actions"
description: 
  In some of my projects, I like to provide an accurate documentation. Which means that I want to have examples and documentation up to date.

  So, when I'm updating a library or a service I'm using in my code, I need to manually find and replace all the text to reflect the changes.
  
  This post describes how you can do this automatically using Github Actions, Maven and Dependabot.
toc: true
authors:
  - David Pilato
tags:
  - github
  - documentation
  - maven
categories:
  - tutorial
  - tips
date: 2023-01-12T10:47:07+01:00
featuredImage: blog/2023-01-12-automatically-update-documentation-with-github-actions/overview.png
draft: false
---

In some of my projects, I like to provide an accurate documentation. Which means that I want to have examples and documentation up to date.

So, when I'm updating a library or a service I'm using in my code, I need to manually find and replace all the text to reflect the changes.

For example, let say I have `README.md` with:

```markdown
We have the following versions:

* Current is 1.0-SNAPSHOT.
* This project is tested with Elasticsearch 8.5.1.
```

And a `.env` file which I'm using to run `docker compose`:

```text
STACK_VERSION=8.5.1
```

When you need to update a version, let say Elasticsearch to `8.5.2`, you need to edit your `pom.xml` and also all related files like the `.env` file.

This can be error prone or you can just forget about a file. It would be better to just update the property somewhere and let the project automatically update the other files.

## Maven resources plugin to the rescue

This can be easily done with the [maven resources plugin](https://maven.apache.org/plugins/maven-resources-plugin/). The only thing to write is something like that:

```xml
<properties>
  <elasticsearch.version>8.5.1</elasticsearch.version>
</properties>

<build>
  <resources>
    <resource>
      <directory>src/main/documentation</directory>
      <filtering>true</filtering>
      <targetPath>${project.basedir}</targetPath>
    </resource>
  </resources>
</build>
```

Any file available within `src/main/documentation` dir will be copy to the root project dir and filtered with the different maven properties. Define a `src/main/documentation/README.md` file:

```markdown
We have the following versions:

* Current is ${project.version}.
* This project is tested with Elasticsearch ${elasticsearch.version}.
```

Define a `src/main/documentation/.env` file:

```text
STACK_VERSION=${elasticsearch.version}
```

When processing the resources within the `process-resources` phase, maven will replace the maven properties by the right values:

```shell
mvn process-resources
```

And you will see that `README.md` and `.env` have been updated to reflect the changes if any. Actually, you won't see anything unless you update a version. 😉

So the process is now:

* Update the `pom.xml`
* Run `mvn process-resources`
* Commit the changes

## Automatic update with Github Actions

To avoid having to locally checkout a branch that has been created in Github, run the maven command and git push the changes to the branch before it can be reviewed and merged, we can use Github Actions to update our resources automatically.

Let say that we already have an action `.github/workflows/main.yml` file:

```yml
name: Build the project
on: [push, pull_request]
jobs:
  update-files:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Set up JDK 17 and Maven Central Repository
        uses: actions/setup-java@v2
        with:
          java-version: '17'
          distribution: 'adopt'
          cache: 'maven'
      - name: Build the project
        run: mvn -B install
```

This is performing the following steps:

* Checkout
* Setup the JDK and Maven cache
* Build the project

We need to add the generation of the updated files just before building the project:

```yml
- name: Update resources with Maven
  run: mvn -B process-resources
- name: Build the project
  run: mvn -B install
```

And then we need to commit our changes. For this we will use the [git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action):

```yml
- name: Update resources with Maven
  run: mvn -B process-resources
- name: Update files if needed
  uses: stefanzweifel/git-auto-commit-action@v4
- name: Build the project
  run: mvn -B install
```

But actually this will fail. Because we need to define that we want to have a write access to the repository:

```yml
permissions:
  contents: write
  packages: write
```

In the context of a PR, the checkout is by default done using another branch name than the real branch name. When the plugin commits the changes, it does not go to the branch associated with the PR.

On non-push events, such as `pull_request`, we need to specify the actual branch name of the pr as the `ref` for the checkout:

```yml
- name: Checkout code
  uses: actions/checkout@v3
  with:
    ref: ${{ github.head_ref }}
```

## Manually create a PR

Let's update the `pom.xml` and update Elasticsearch version to `8.5.2`:

```xml
<elasticsearch.version>8.5.2</elasticsearch.version>
```

Then commit it and push it to a branch. And finally create [a PR](https://github.com/dadoonet/demo-automatic-doc/pull/1):

{{< figure src="pr-overview.png" caption="Update the version manually" >}}

So we have one single commit:

{{< figure src="pr-initial-commit.png" caption="One single commit" >}}

When the [Github Actions workflow starts](https://github.com/dadoonet/demo-automatic-doc/actions/runs/3906707095/jobs/6675166018), it updates the code, commits it and pushes it to our branch which is now updated:

{{< figure src="pr-commits.png" caption="With the additional commit" >}}

## Using Dependabot to update our versions

If you are using [Dependabot](https://docs.github.com/en/code-security/dependabot/) to automatically update your libraries, the same update process should happen. If you don't, go to the repository settings and enable Dependabot version updates:

{{< figure src="dependabot-enable.png" caption="Enable Dependabot" >}}

So we have the following `.github/dependabot.yml` file:

```yml
version: 2
updates:
  - package-ecosystem: "maven"
    directory: "/"
    schedule:
      interval: "daily"
```

This automatically creates a PR when a new version is available.

## Dependabot and Github actions

When we commit the changes, it does not trigger another github action call. This is due to [limitations set by GitHub](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#using-the-github_token-in-a-workflow). This prevents us from accidentally creating recursive workflow runs. But here, we want that.

So we need to create a new Personal Access Token (PAT) instead of the default `GITHUB_TOKEN`. Open your [Github Developper Settings](https://github.com/settings/apps) and create a new Personal Access Token. It needs to have the `repo` and `workflow` scopes:

{{< figure src="settings-add-pat.png" caption="Create your Personal Access Token" >}}

Note the generated token and store it as a secret in the repository.

{{< figure src="secrets-add-pat.png" caption="Add your new secret" >}}

Then pass the new token to the checkout step:

```yml
- name: Checkout code
  uses: actions/checkout@v3
  with:
    ref: ${{ github.head_ref }}
    token: ${{ secrets.PAT }}
```

But when dependabot runs the action, it runs it under another context. So you need to create the `PAT` secret under the Dependabot context as well:

{{< figure src="secrets-dependabot-pat.png" caption="Add your secret to Dependabot context" >}}

Here is what happens when [dependabot creates a PR](https://github.com/dadoonet/demo-automatic-doc/pull/2).

{{< figure src="dependabot-overview.png" caption="The PR" >}}

Note that few seconds after Dependabot has created the PR, it has been updated by our job:

{{< figure src="dependabot-build-details.png" caption="Build details" >}}

And we can see the details of the commit that has been added by Github Actions on behalf of Dependabot:

{{< figure src="dependabot-last-commit.png" caption="Automatically added commit" >}}

## The full workflow

The final workflow is:

```yml
name: Build the project
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      packages: write
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          ref: ${{ github.head_ref }}
          token: ${{ secrets.PAT }}
      - name: Update resources with Maven
        run: mvn -B process-resources
      - name: Update files if needed
        uses: stefanzweifel/git-auto-commit-action@v4
      - name: Set up JDK 17 and Maven Central Repository
        uses: actions/setup-java@v2
        with:
          java-version: '17'
          distribution: 'adopt'
          cache: 'maven'
      - name: Build the project
        run: mvn -B install
```

You can see this code in the [dadoonet/demo-automatic-doc](https://github.com/dadoonet/demo-automatic-doc) demo repository.
