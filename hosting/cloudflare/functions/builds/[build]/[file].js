import manifest from '../../../build-manifest.json';

const POLICY = 'public, max-age=31536000, immutable, no-transform';
const LARGE = new Set(['index.wasm', 'index.pck']);

// Only this content-addressed build is exposed. The generated loader and all
// small files remain byte-for-byte ordinary static assets beside these routes.
export async function onRequest({ request, env, params, waitUntil }) {
  const { build, file } = params;
  const artifact = manifest.files.find((entry) => entry.name === file);
  if (build !== manifest.build_id || !LARGE.has(file) || !artifact) {
    return new Response('Unknown artifact', { status: 404 });
  }
  if (!['GET', 'HEAD'].includes(request.method)) {
    return new Response('Method not allowed', {
      status: 405, headers: { Allow: 'GET, HEAD' },
    });
  }

  // Deliberately serve full bodies (200), including requests carrying Range.
  // Godot's ordinary loader fetches the whole files. Do not cache partial packs.
  // Queries and client headers do not create additional copies of immutable data.
  const url = new URL(request.url);
  url.search = '';
  const cacheKey = new Request(url.toString());
  const cached = await caches.default.match(cacheKey);
  if (cached) {
    const response = new Response(request.method === 'HEAD' ? null : cached.body, cached);
    response.headers.set('X-Hush-Cache', 'HIT');
    return response;
  }

  const key = `builds/${build}/${file}`;
  const object = await env.HUSH_ARTIFACTS[request.method === 'HEAD' ? 'head' : 'get'](key);
  if (!object) return new Response('Artifact missing', { status: 404 });
  if (object.size !== artifact.bytes) {
    if (object.body) await object.body.cancel();
    return new Response('Artifact size mismatch', { status: 502 });
  }
  const headers = new Headers({
    'Content-Type': file.endsWith('.wasm') ? 'application/wasm' : 'application/octet-stream',
    'Content-Length': String(object.size),
    'Cache-Control': POLICY,
    'Accept-Ranges': 'none',
    ETag: `"sha256-${artifact.sha256}"`,
    'X-Content-Type-Options': 'nosniff',
    'X-Robots-Tag': 'noindex, nofollow, noarchive',
    'X-Hush-Build': build,
    'X-Hush-SHA256': artifact.sha256,
    'X-Hush-Cache': 'MISS',
    'X-Hush-Cached-At': new Date().toISOString(),
  });
  // R2's body is a ReadableStream. Never materialize the WASM/PCK in JS memory.
  const response = new Response(request.method === 'HEAD' ? null : object.body, { headers });
  if (request.method === 'GET') {
    waitUntil(caches.default.put(cacheKey, response.clone()).catch((error) => {
      console.error('Hush artifact cache put failed', String(error));
    }));
  }
  return response;
}
