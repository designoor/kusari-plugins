type PaymentStatus = "pending" | "completed" | "failed" | "refunded";

function getBadgeColor(status: PaymentStatus): string {
  switch (status) {
    case "pending":
      return "yellow";
    case "completed":
      return "green";
    case "failed":
      return "red";
    case "refunded":
      return "blue";
    default: {
      const _exhaustive: never = status;
      return "gray";
    }
  }
}

export { getBadgeColor };
export type { PaymentStatus };
