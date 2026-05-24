import { AlertCircle } from 'lucide-react';

export default function Placeholder({ title, description = 'En construcción' }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] bg-white rounded-xl shadow-sm p-8">
      <AlertCircle className="h-16 w-16 text-gray-400 mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
      <p className="text-gray-600 text-center max-w-md">{description}</p>
      <p className="text-sm text-gray-500 mt-4">Esta funcionalidad estará disponible próximamente</p>
    </div>
  );
}
