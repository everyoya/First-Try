import Image from "next/image";

const features = [
  {
    title: "Next.js + TypeScript",
    description: "Ready to build fast, typed UI with the App Router enabled by default.",
  },
  {
    title: "Express server",
    description: "Simple Express app with dotenv support for quick backend routes.",
  },
  {
    title: "Prettier + ESLint",
    description: "Opinionated formatting and linting rules to keep the codebase consistent.",
  },
];

export default function HomePage() {
  return (
    <>
      <Image
        src="/next.svg"
        alt="Next.js Logo"
        width={180}
        height={37}
        priority
      />
      <h1>First Try scaffold</h1>
      <p>
        Start the Next.js dev server with <code>npm run dev</code> and the Express API with
        <code> npm run server</code> once dependencies are installed.
      </p>
      <section style={{ display: "grid", gap: "1rem" }}>
        {features.map((feature) => (
          <article
            key={feature.title}
            style={{
              border: "1px solid #e5e5e5",
              borderRadius: "8px",
              padding: "1rem 1.25rem",
              maxWidth: "540px",
            }}
          >
            <h2 style={{ margin: "0 0 0.5rem" }}>{feature.title}</h2>
            <p style={{ margin: 0 }}>{feature.description}</p>
          </article>
        ))}
      </section>
    </>
  );
}
