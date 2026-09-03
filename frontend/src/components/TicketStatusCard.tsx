/**
 * TicketStatusCard component for rendering ticket status responses
 * Reference: specs/013-react-frontend-chat/plan.md (T014)
 */

import React from 'react';
import { TicketStatusPayload } from '../types/toolPayloads';

interface TicketStatusCardProps {
  data: TicketStatusPayload;
}

export const TicketStatusCard: React.FC<TicketStatusCardProps> = ({ data }) => {
  const statusColors: Record<string, string> = {
    open: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    resolved: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800',
  };
  const statusColor = statusColors[data.status] ?? 'bg-gray-100 text-gray-800';

  const priorityColors: Record<string, string> = {
    low: 'bg-green-50',
    medium: 'bg-yellow-50',
    high: 'bg-red-50',
  };
  const priorityColor = priorityColors[data.priority] ?? 'bg-gray-50';

  return (
    <div className={`${priorityColor} border border-gray-300 rounded-lg p-4 max-w-md`}>
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="text-sm font-semibold text-gray-600">Ticket ID</div>
          <div className="text-lg font-bold text-gray-900">{data.ticket_id}</div>
        </div>
        <span className={`${statusColor} px-3 py-1 rounded-full text-sm font-medium`}>
          {data.status}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="text-sm font-semibold text-gray-600">Summary</div>
          <div className="text-gray-900">{data.summary}</div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="text-sm font-semibold text-gray-600">Category</div>
            <div className="text-gray-900">{data.category}</div>
          </div>
          <div>
            <div className="text-sm font-semibold text-gray-600">Priority</div>
            <div className="text-gray-900 font-medium">{data.priority}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
