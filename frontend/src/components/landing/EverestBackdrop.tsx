type EverestBackdropProps = {
  fixed?: boolean;
  animate?: boolean;
  className?: string;
  overlayClassName?: string;
};

export function EverestBackdrop({
  fixed = true,
  animate = true,
  className = "",
  overlayClassName = "",
}: EverestBackdropProps) {
  return (
    <div className={`absolute inset-0 overflow-hidden ${className}`} aria-hidden>
      <div
        className={`everest-bg absolute inset-0 ${fixed ? "everest-bg-fixed" : ""} ${
          animate ? "everest-ken-burns" : ""
        }`}
      />
      <div className={`everest-overlay absolute inset-0 ${overlayClassName}`} />
    </div>
  );
}
