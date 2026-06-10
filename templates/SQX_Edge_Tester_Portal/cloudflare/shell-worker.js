const LOCKED_HEADERS = {
  "content-type": "text/plain; charset=utf-8",
  "cache-control": "no-store, max-age=0",
  "x-content-type-options": "nosniff",
  "x-frame-options": "DENY",
  "referrer-policy": "no-referrer",
  "robots": "noindex, nofollow",
};

export default {
  async fetch() {
    return new Response("SQX Edge tester shell locked. No application is published here.", {
      status: 404,
      headers: LOCKED_HEADERS,
    });
  },
};
