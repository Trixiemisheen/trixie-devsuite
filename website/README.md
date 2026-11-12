# Trixie Misheen website

This is a standalone static website for `trixiemisheen.site`. It is intentionally
separate from the DevSuite application and can be deployed independently.

## Preview locally

From the repository root:

```powershell
cd website
python -m http.server 8080
```

Open <http://localhost:8080> in a browser.

## Publish with GitHub Pages

1. Push this repository to GitHub.
2. Open the repository's **Settings → Pages**.
3. Under **Build and deployment**, choose **GitHub Actions**.
4. Run the **Deploy website** workflow manually once, or push a change under
   `website/` to trigger it.
5. Keep the included `CNAME` file at the published site root.
6. In your domain registrar's DNS panel, add:

   - `A` records for `@` pointing to GitHub Pages' current IP addresses
   - a `CNAME` record for `www` pointing to your GitHub Pages hostname

   GitHub will show the exact DNS values in **Settings → Pages → Custom domain**.
   Enable HTTPS after DNS finishes propagating.

Do not put registrar passwords, API tokens, or private keys in this repository.
