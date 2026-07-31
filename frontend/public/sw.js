const WORKER_VERSION = "return-loop-v1";
const PUSH_ENABLED = false;

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) =>
  event.waitUntil(self.clients.claim()),
);
self.addEventListener("push", (event) => {
  if (!PUSH_ENABLED) return;
  const payload = event.data?.json() ?? {};
  event.waitUntil(
    self.registration.showNotification("Fictional world update", {
      body: "A source-linked update is available in your private inbox.",
      tag: String(payload.logicalId ?? WORKER_VERSION),
      silent: true,
      data: { path: "/#return-loop-title" },
    }),
  );
});
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.openWindow("/#return-loop-title"));
});
