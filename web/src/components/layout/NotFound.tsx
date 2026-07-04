import { Link } from 'react-router-dom';
import { ArrowLeft, SearchX } from 'lucide-react';

export const NotFound = () => (
  <section className="min-h-[80vh] pt-32 pb-20 px-6 flex items-center justify-center">
    <div className="text-center max-w-md">
      <SearchX size={64} className="text-slate-600 mx-auto mb-6" />
      <h1 className="text-4xl font-black text-white mb-4">Página não encontrada</h1>
      <p className="text-slate-400 mb-8">
        A rota que você tentou acessar não existe. Verifique o endereço ou volte ao início.
      </p>
      <Link
        to="/"
        className="btn-premium premium-gradient text-white px-8 py-3 rounded-xl text-sm font-bold inline-flex items-center gap-2"
      >
        <ArrowLeft size={16} /> Voltar ao Início
      </Link>
    </div>
  </section>
);