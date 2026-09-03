/**
 * PasswordResetCard component for rendering password reset responses
 * Reference: specs/013-react-frontend-chat/plan.md (T015)
 */

import React from 'react';
import { PasswordResetPayload } from '../types/toolPayloads';

interface PasswordResetCardProps {
  data: PasswordResetPayload;
}

export const PasswordResetCard: React.FC<PasswordResetCardProps> = ({ data }) => {
  const isEscalated = data.escalation_reason !== null;
  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    denied: 'bg-red-100 text-red-800',
    completed: 'bg-blue-100 text-blue-800',
  };
  const statusColor = statusColors[data.status] ?? 'bg-gray-100 text-gray-800';

  return (
    <div className={`${isEscalated ? 'bg-red-50' : 'bg-green-50'} border border-gray-300 rounded-lg p-4 max-w-md`}>
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="text-sm font-semibold text-gray-600">Password Reset</div>
          <div className="text-lg font-bold text-gray-900">Request</div>
        </div>
        <span className={`${statusColor} px-3 py-1 rounded-full text-sm font-medium`}>
          {data.status}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="text-sm font-semibold text-gray-600">Temporary Password Note</div>
          <div className="text-gray-900 bg-white px-3 py-2 rounded border border-gray-200">
            {data.temporary_password_note}
          </div>
        </div>

        {isEscalated && (
          <div>
            <div className="text-sm font-semibold text-red-700">Escalation Reason</div>
            <div className="text-red-900 bg-white px-3 py-2 rounded border border-red-200">
              {data.escalation_reason}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
