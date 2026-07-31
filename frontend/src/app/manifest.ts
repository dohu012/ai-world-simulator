import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Gray Harbor World Observer",
    short_name: "Gray Harbor",
    description: "A privacy-preserving fictional world observer.",
    start_url: "/",
    display: "standalone",
    background_color: "#020617",
    theme_color: "#0f172a",
  };
}
