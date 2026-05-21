import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { createReadStream, existsSync } from 'node:fs';
import path from 'node:path';
import { resolveStaticFilePath } from './src/core/static-server.js';

const port = process.env.PORT || 3000;
const root = process.cwd();

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8'
};

const server = http.createServer(async (req, res) => {
  try {
    const filePath = resolveStaticFilePath(req.url || '/', { rootDir: root });

    if (!filePath) {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Forbidden');
      return;
    }

    if (!existsSync(filePath)) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }

    const ext = path.extname(filePath);
    res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain; charset=utf-8' });
    createReadStream(filePath).pipe(res);
  } catch (error) {
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(`Server error: ${error instanceof Error ? error.message : 'unknown'}`);
  }
});

server.listen(port, async () => {
  const indexHtml = await readFile(path.join(root, 'public', 'index.html'), 'utf8');
  if (!indexHtml.includes('/src/ui/app.js')) {
    console.warn('Warning: public/index.html is missing /src/ui/app.js reference');
  }
  console.log(`Life AB Test running at http://localhost:${port}`);
});
