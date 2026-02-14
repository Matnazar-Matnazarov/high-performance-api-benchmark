/**
 * Timing middleware: X-Server-Time, X-Response-Time (Bolt-compatible).
 * Wraps res.end to set headers before sending.
 */

export function timingMiddleware(req, res, next) {
  const start = performance.now();
  res.setHeader("X-Server-Time", new Date().toISOString());

  const origEnd = res.end;
  res.end = function (chunk, encoding, callback) {
    if (!res.headersSent) {
      const durationMs = (performance.now() - start).toFixed(2);
      res.setHeader("X-Response-Time", `${durationMs}ms`);
    }
    return origEnd.call(this, chunk, encoding, callback);
  };
  next();
}
