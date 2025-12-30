# Configuration CORS pour Google Cloud Storage

Ce site charge des PDFs depuis Google Cloud Storage (`dadoonet-talks` bucket). Pour que PDF.js puisse charger ces fichiers depuis le navigateur, il est nécessaire de configurer les en-têtes CORS sur le bucket.

## Configuration via gsutil (recommandé)

1. Créez un fichier `cors.json` avec le contenu suivant :

```json
[
  {
    "origin": [
      "https://david.pilato.fr",
      "https://dadoonet.github.io",
      "http://localhost:1313"
    ],
    "method": ["GET", "HEAD", "OPTIONS"],
    "responseHeader": [
      "Content-Type",
      "Content-Length",
      "Content-Range",
      "Accept-Ranges",
      "Access-Control-Allow-Origin",
      "Access-Control-Allow-Methods",
      "Access-Control-Allow-Headers"
    ],
    "maxAgeSeconds": 3600
  }
]
```

2. Appliquez la configuration CORS au bucket :

```bash
gsutil cors set cors.json gs://dadoonet-talks
```

3. Vérifiez la configuration :

```bash
gsutil cors get gs://dadoonet-talks
```

## Configuration via la Console Google Cloud

1. Allez dans [Google Cloud Console](https://console.cloud.google.com/)
2. Naviguez vers **Cloud Storage** > **Buckets**
3. Sélectionnez le bucket `dadoonet-talks`
4. Allez dans l'onglet **Permissions**
5. Cliquez sur **Edit CORS configuration**
6. Ajoutez la configuration suivante :

```json
[
  {
    "origin": [
      "https://david.pilato.fr",
      "https://dadoonet.github.io",
      "http://localhost:1313"
    ],
    "method": ["GET", "HEAD", "OPTIONS"],
    "responseHeader": [
      "Content-Type",
      "Content-Length",
      "Content-Range",
      "Accept-Ranges",
      "Access-Control-Allow-Origin",
      "Access-Control-Allow-Methods",
      "Access-Control-Allow-Headers"
    ],
    "maxAgeSeconds": 3600
  }
]
```

7. Cliquez sur **Save**

## Explication des paramètres

- **origin** : Les domaines autorisés à faire des requêtes CORS. **Important** : Google Cloud Storage ne supporte pas les wildcards (`*`) dans les origines. Vous devez lister explicitement chaque domaine (ex: `https://dadoonet.github.io` au lieu de `https://*.github.io`).
- **method** : Les méthodes HTTP autorisées. `GET`, `HEAD` et `OPTIONS` sont nécessaires pour les requêtes CORS.
- **responseHeader** : Les en-têtes de réponse que le navigateur est autorisé à lire. Inclut les en-têtes CORS standards.
- **maxAgeSeconds** : Durée de mise en cache de la réponse preflight (3600 secondes = 1 heure).

## Notes importantes

⚠️ **Google Cloud Storage ne supporte pas les wildcards dans les origines CORS**. Vous devez lister explicitement chaque domaine. Si vous avez plusieurs sous-domaines GitHub Pages, ajoutez-les tous individuellement.

## Vérification

Après avoir configuré CORS, testez en ouvrant la console du navigateur (F12) et vérifiez qu'il n'y a plus d'erreurs CORS lors du chargement des PDFs.

## Dépannage

### Vérifier que la configuration CORS est appliquée

```bash
gsutil cors get gs://dadoonet-talks
```

Vous devriez voir votre configuration JSON. Si vous voyez `[]` ou rien, la configuration n'a pas été appliquée.

### Vérifier les permissions du bucket

Les fichiers doivent être accessibles publiquement. Vérifiez que le bucket autorise la lecture publique :

```bash
# Vérifier les permissions IAM du bucket
gsutil iam get gs://dadoonet-talks

# Si nécessaire, rendre les fichiers accessibles publiquement
gsutil iam ch allUsers:objectViewer gs://dadoonet-talks
```

Ou pour un objet spécifique :
```bash
gsutil acl ch -u AllUsers:R gs://dadoonet-talks/slides/2012/2012-10-13-elasticsearch-osdc.pdf
```

### Tester avec curl

Testez si les en-têtes CORS sont présents :

```bash
curl -I -H "Origin: http://localhost:1313" \
  https://storage.googleapis.com/dadoonet-talks/slides/2012/2012-10-13-elasticsearch-osdc.pdf
```

Vous devriez voir `Access-Control-Allow-Origin: http://localhost:1313` dans les en-têtes de réponse.

### Problèmes courants

1. **La configuration n'a pas été appliquée** : Vérifiez avec `gsutil cors get`
2. **Les fichiers ne sont pas publics** : Vérifiez les permissions IAM/ACL
3. **Cache du navigateur** : Videz le cache ou testez en navigation privée
4. **Propagation** : Attendez quelques secondes après avoir appliqué la configuration

## Références

- [Documentation Google Cloud Storage CORS](https://cloud.google.com/storage/docs/configuring-cors)
- [Documentation gsutil cors](https://cloud.google.com/storage/docs/gsutil/commands/cors)

