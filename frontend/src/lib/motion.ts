export const spring = {
  /** UI micro-interactions — buttons, toggles (150ms equivalent) */
  snappy: { type: "spring" as const, stiffness: 400, damping: 30 },
  /** Panel transitions, sidebar drawer */
  smooth: { type: "spring" as const, stiffness: 200, damping: 25 },
  /** Landing hero, onboarding tour */
  gentle: { type: "spring" as const, stiffness: 120, damping: 20 },
};

export const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

export const stagger = {
  visible: { transition: { staggerChildren: 0.08 } },
};
