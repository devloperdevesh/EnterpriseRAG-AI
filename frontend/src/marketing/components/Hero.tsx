import FloatingSphere from "./FloatingSphere";
import ParticlesBg from "./ParticlesBg";
import React from "react";

export default function Home() {
  return (
    <div className="bg-white text-gray-900">

      {/* HERO */}
      <section className="text-center py-20 px-6 max-w-5xl mx-auto">
        <h1 className="text-4xl md:text-5xl font-semibold leading-tight">
          AI-Powered Document Intelligence
        </h1>
        <p className="mt-6 text-lg text-gray-600">
          Search, analyze, and understand your documents using natural language.
          Get instant, context-aware answers powered by a high-performance RAG system.
        </p>

        <div className="mt-8 flex justify-center gap-4">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium">
            Start Free Trial
          </button>
          <button className="border border-gray-300 px-6 py-3 rounded-lg font-medium">
            View Demo
          </button>
        </div>
      </section>

      {/* METRICS */}
      <section className="border-t border-b py-10 text-center">
        <div className="flex flex-wrap justify-center gap-10 text-sm text-gray-600">
          <span>10M+ Documents</span>
          <span>60+ Countries</span>
          <span>&lt;500ms Response</span>
          <span>Production Ready</span>
        </div>
      </section>

      {/* FEATURES */}
      <section className="py-20 px-6 max-w-6xl mx-auto">
        <h2 className="text-3xl font-semibold text-center mb-12">
          Powerful AI Features
        </h2>

        <div className="grid md:grid-cols-2 gap-10">

          <div>
            <h3 className="font-semibold text-lg">Multi-Format Processing</h3>
            <p className="text-gray-600 mt-2">
              Upload PDFs, Word, Excel, images, and scanned documents with OCR support.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-lg">Semantic Search</h3>
            <p className="text-gray-600 mt-2">
              Find answers by meaning using vector embeddings and similarity search.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-lg">Sub-Second Responses</h3>
            <p className="text-gray-600 mt-2">
              Optimized RAG pipeline delivers answers in under 500ms.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-lg">Source-Cited Answers</h3>
            <p className="text-gray-600 mt-2">
              Every response is grounded in your documents with full traceability.
            </p>
          </div>

        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="bg-gray-50 py-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-3xl font-semibold mb-10">How It Works</h2>

          <div className="grid md:grid-cols-3 gap-8 text-left">

            <div>
              <h4 className="font-semibold">1. Upload</h4>
              <p className="text-gray-600 mt-2">
                Documents are chunked into optimized segments.
              </p>
            </div>

            <div>
              <h4 className="font-semibold">2. Retrieve</h4>
              <p className="text-gray-600 mt-2">
                Queries are matched using vector search.
              </p>
            </div>

            <div>
              <h4 className="font-semibold">3. Generate</h4>
              <p className="text-gray-600 mt-2">
                AI generates grounded, context-aware responses.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* PRICING */}
      <section className="py-20 px-6 max-w-6xl mx-auto text-center">
        <h2 className="text-3xl font-semibold mb-12">Pricing</h2>

        <div className="grid md:grid-cols-3 gap-8">

          <div className="border rounded-xl p-6">
            <h3 className="font-semibold">Starter</h3>
            <p className="text-2xl mt-4">$49/mo</p>
            <p className="text-gray-600 mt-2">100 documents</p>
          </div>

          <div className="border-2 border-blue-600 rounded-xl p-6">
            <h3 className="font-semibold">Professional</h3>
            <p className="text-2xl mt-4">$149/mo</p>
            <p className="text-gray-600 mt-2">1,000 documents</p>
          </div>

          <div className="border rounded-xl p-6">
            <h3 className="font-semibold">Enterprise</h3>
            <p className="text-2xl mt-4">Custom</p>
            <p className="text-gray-600 mt-2">Unlimited usage</p>
          </div>

        </div>
      </section>

      {/* CTA */}
      <section className="bg-blue-600 text-white text-center py-16">
        <h2 className="text-2xl font-semibold">
          Start building with AI-powered document intelligence
        </h2>
        <div className="mt-6">
          <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium">
            Get Started
          </button>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-10 text-center text-gray-500 text-sm">
        © 2026 Multi-Lens RAG. All rights reserved.
      </footer>

    </div>
  );
}
