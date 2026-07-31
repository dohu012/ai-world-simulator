import { PlaytestShell } from "@/features/product-validation/playtest-shell";

export const metadata = {
  title: "Gray Harbor fictional-world playtest",
  robots: { index: false, follow: false },
};

export default function PlaytestPage() {
  return <PlaytestShell />;
}
