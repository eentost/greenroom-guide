# Greenroom Guide: legacy Pages URLs

The live content is now published at https://eentost.github.io/. This repository
only publishes one-to-one redirect pages for the former
https://eentost.github.io/greenroom-guide/ addresses, including the old home page's
`index.html` alias. GitHub Pages serves these static HTML files with HTTP 200;
the browser follows an immediate meta refresh. The same destination also
appears in the canonical annotation and in a visible link. These are not HTTP
301 responses.

The project publishing workflow does not expose the old guides, ad markup, or
project sitemap. A custom 404 page handles removed or unknown URLs and links
to the current site. The original archive is retained in Git at
`.deploy/site.tar.gz`, outside the artifact. Crawlers are allowed to read the
redirect pages. The active sitemap is https://eentost.github.io/sitemap.xml.

Build and validate locally in a fresh directory:

```sh
out="$(mktemp -d)/site" && python3 scripts/build_redirects.py "$out" && python3 scripts/verify_redirects.py "$out"
```
