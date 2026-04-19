type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded';

function getPaymentBadgeColor(status: PaymentStatus): string {
  switch (status) {
    case 'pending':
      return 'yellow';
    case 'completed':
      return 'green';
    case 'failed':
      return 'red';
    case 'refunded':
      return 'blue';
    default:
      return 'gray';
  }
}
