
import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchSchemes() {
      try {
        const response = await fetch(`${API_URL}/api/schemes`);

        if (!response.ok) {
          throw new Error("Failed to fetch schemes");
        }

        const data = await response.json();
        setSchemes(data.schemes);
      } catch (err) {
        setError(err.message || "Unable to connect to the server");
      } finally {
        setLoading(false);
      }
    }

    fetchSchemes();
  }, []);

  return (
    <main className="container">
      <header className="header">
        <p className="eyebrow">YOUR GOVERNMENT SCHEME COMPANION</p>
        <h1>Discover Schemes with SchemeWise</h1>
        <p>
          Explore schemes and understand their requirements
          in one place.
        </p>
      </header>

      {loading && <p>Loading schemes...</p>}

      {error && (
        <p role="alert">
          {error}. Check whether the backend is running.
        </p>
      )}

      {!loading && !error && (
        <>
          <p>{schemes.length} schemes available</p>

          <section className="scheme-grid">
            {schemes.map((scheme) => (
              <article className="scheme-card" key={scheme.id}>
                <span className="category">
                  {scheme.category}
                </span>

                <h2>{scheme.name}</h2>

                <p>{scheme.description}</p>

                <p>
                  <strong>Region:</strong> {scheme.state}
                </p>

                {scheme.official_url && (
                  <a
                    href={scheme.official_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Visit official website
                  </a>
                )}
              </article>
            ))}
          </section>
        </>
      )}
    </main>
  );
}

export default App;
