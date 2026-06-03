import { Button } from "../components/Button";

export function Home() {
  return (
    <main className="home-page">
      <h1>Welcome to MergeFlow</h1>
      <p>Review generated API specs faster with lightweight UI polish.</p>
      <Button label="Review latest results" />
    </main>
  );
}
