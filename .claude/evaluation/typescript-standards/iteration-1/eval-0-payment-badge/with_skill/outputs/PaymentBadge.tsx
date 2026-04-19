const paymentStatuses = ["pending", "completed", "failed", "refunded"] as const;
type PaymentStatus = (typeof paymentStatuses)[number];

type BadgeColor = "yellow" | "green" | "red" | "blue";

const badgeColorByStatus: Record<PaymentStatus, BadgeColor> = {
  pending: "yellow",
  completed: "green",
  failed: "red",
  refunded: "blue",
};

export function getBadgeColor(status: PaymentStatus): BadgeColor {
  return badgeColorByStatus[status];
}
