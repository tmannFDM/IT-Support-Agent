import { PERSONAS } from '../constants';

interface PersonaSelectorProps {
  selectedPersonaId: string;
  onChange: (personaId: string) => void;
  disabled: boolean;
}

export function PersonaSelector({
  selectedPersonaId,
  onChange,
  disabled,
}: PersonaSelectorProps) {
  return (
    <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
      Persona
      <select
        value={selectedPersonaId}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100"
      >
        {PERSONAS.map((persona) => (
          <option key={persona.id} value={persona.id}>
            {persona.displayName}
          </option>
        ))}
      </select>
    </label>
  );
}