# Wordreader

A minimalist browser-based reader for Word documents, with search, zoom, an outline, printing, and support for document formatting and images.

## Formats and privacy

- **DOCX** files are rendered in the browser using docx-preview; the document is not uploaded.
- **DOC** files (up to 20 MB) are sent to the conversion endpoint, converted to DOCX with LibreOffice, and rendered in the browser. The service uses temporary files that are removed after conversion.

Complex formatting may differ from Microsoft Word. Password-protected documents are not supported.

## Deployment

Serve `dist/` as a static site. Its JavaScript loads JSZip and docx-preview from jsDelivr. For DOC support, install Python 3 and LibreOffice Writer, install `server/converter.py` at `/opt/wordreader/converter.py`, and install and start `server/wordreader-converter.service` with systemd. The service listens on `127.0.0.1:8793`; expose only its `/convert` endpoint through the same origin as the static site. Limit request bodies to 20 MB and allow a 75-second upstream timeout. Use HTTPS for the public site.

Example Nginx location inside the site's server block:

```nginx
location = /convert {
    client_max_body_size 20m;
    proxy_request_buffering off;
    proxy_buffering off;
    proxy_read_timeout 75s;
    access_log off;
    proxy_pass http://127.0.0.1:8793;
}
```

The service unit uses systemd sandboxing and limits its memory and CPU usage. Review these settings and your network and security configuration for your deployment.
