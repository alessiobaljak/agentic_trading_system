'use client';

/**
 * La colonna dei grafici a barre (skill dataviz, marks-and-anatomy.md): l'estremo arrotondato di 4 px dalla parte del dato, la base
 * dritta sulla linea dello zero, che sia positiva o negativa. Si passa a `<Bar shape={<Colonna />} />`.
 */
export function Colonna(props: {
  x?: number; y?: number; width?: number; height?: number; fill?: string; value?: unknown; fillOpacity?: number;
}) {
  const { x = 0, y = 0, width = 0, height = 0, fill, fillOpacity } = props;
  const v = Array.isArray(props.value) ? Number(props.value[1]) - Number(props.value[0]) : Number(props.value);
  const h = Math.abs(height);
  if (!Number.isFinite(v) || width <= 0 || h < 0.5) return <g />;
  const alto = Math.min(y, y + height);
  const basso = alto + h;
  const r = Math.min(4, h, width / 2);
  const x1 = x + width;
  const d = v >= 0
    ? `M${x},${basso} L${x},${alto + r} Q${x},${alto} ${x + r},${alto} L${x1 - r},${alto} Q${x1},${alto} ${x1},${alto + r} L${x1},${basso} Z`
    : `M${x},${alto} L${x1},${alto} L${x1},${basso - r} Q${x1},${basso} ${x1 - r},${basso} L${x + r},${basso} Q${x},${basso} ${x},${basso - r} Z`;
  return <path d={d} fill={fill} fillOpacity={fillOpacity} />;
}
