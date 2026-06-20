export const spring = {
  snappy: { type: "spring" as const, stiffness: 400, damping: 30 },
  smooth: { type: "spring" as const, stiffness: 200, damping: 25 },
  gentle: { type: "spring" as const, stiffness: 120, damping: 20 },
};

export const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

export const stagger = {
  visible: { transition: { staggerChildren: 0.08 } },
};
