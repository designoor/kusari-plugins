import React from 'react';

export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';

const BADGE_COLORS: Record<PaymentStatus, string> = {
  pending: 'yellow',
  completed: 'green',
  failed: 'red',
  refunded: 'blue',
};

export function getPaymentBadgeColor(status: PaymentStatus): string {
  return BADGE_COLORS[status];
}

interface PaymentBadgeProps {
  status: PaymentStatus;
}

export function PaymentBadge({ status }: PaymentBadgeProps): React.JSX.Element {
  const color = getPaymentBadgeColor(status);
  return (
    <span className={`badge badge--${color}`}>
      {status}
    </span>
  );
}
