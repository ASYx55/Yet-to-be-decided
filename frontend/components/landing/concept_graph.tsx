"use client";

import { useMemo } from "react";


const nodes = [
    { label: "Pointers", percent: 20, x: 15, y: 22, glow: "#ef4444" },
    { label: "Recursion", percent: 90, x: 48, y: 10, glow: "#8b5cf6" },
    { label: "Sorting", percent: 60, x: 76, y: 24, glow: "#8b5cf6" },

    { label: "Big-O", percent: 70, x: 22, y: 50, glow: "#8b5cf6" },
    { label: "DP", percent: 40, x: 50, y: 46, glow: "#8b5cf6" },
    { label: "Graphs", percent: 30, x: 68, y: 58, glow: "#ef4444" },

    { label: "Trees", percent: 50, x: 25, y: 78, glow: "#f97316" },
    { label: "Vectors", percent: 65, x: 52, y: 88, glow: "#06b6d4" },

    { label: "Derivatives", percent: 80, x: 92, y: 42, glow: "#8b5cf6" },
    { label: "Integrals", percent: 55, x: 82, y: 80, glow: "#8b5cf6" },
];

const links = [
    [0, 3],
    [1, 3],
    [1, 4],
    [1, 2],
    [1, 6],
    [3, 4],
    [3, 6],
    [4, 2],
    [4, 5],
    [4, 7],
    [6, 5],
    [6, 7],
    [2, 5],
    [5, 8],
    [5, 9],
    [8, 9],
];

export function ConceptGraph() {
    const stars = useMemo(() =>
        Array.from({ length: 140 }, (_, i) => {
            const rand = (seed: number) => {
                let x = Math.sin(seed) * 10000;
                return x - Math.floor(x);
            };

            const x = rand(i + 1);
            const y = rand(i + 2);
            const r = rand(i + 3);
            const o = rand(i + 4);
            const d = rand(i + 5);

            return {
                id: i,
                x: Number((x * 100).toFixed(4)),
                y: Number((y * 100).toFixed(4)),
                r: Number((r * 0.22 + 0.05).toFixed(4)),
                opacity: Number((o * 0.7 + 0.2).toFixed(4)),
                duration: Number((d * 4 + 2).toFixed(2)),
            };
        }),
        []);
    return (
        <div className="rounded-[32px] border border-violet-500/10 bg-[#090d19] p-5">
            <div className="mb-4 flex items-center justify-between">
                <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-2 text-sm">
                    Live Concept Graph
                </div>

                <div className="text-xs text-zinc-500">
                    Knowledge Relationships
                </div>
            </div>

            <div className="relative h-[560px] overflow-hidden rounded-[28px] border border-white/5 bg-[#040715]">
                {/* Nebula */}
                <div
                    className="absolute inset-0"
                    style={{
                        background: `
                            radial-gradient(circle at 50% 50%, rgba(139,92,246,.22), transparent 45%),
                            radial-gradient(circle at 20% 25%, rgba(6,182,212,.08), transparent 35%),
                            radial-gradient(circle at 80% 75%, rgba(168,85,247,.08), transparent 35%)
                        `,
                    }}
                />

                {/* Animated Starfield */}
                <svg
                    className="absolute inset-0 h-full w-full"
                    viewBox="0 0 100 100"
                    preserveAspectRatio="none"
                >
                    {stars.map((star) => (
                        <circle
                            key={star.id}
                            cx={star.x}
                            cy={star.y}
                            r={star.r}
                            fill="white"
                        >
                            <animate
                                attributeName="opacity"
                                values={`${star.opacity};0.05;${star.opacity}`}
                                dur={`${star.duration}s`}
                                repeatCount="indefinite"
                            />
                        </circle>
                    ))}
                </svg>

                {/* Vignette */}
                <div
                    className="absolute inset-0"
                    style={{
                        background:
                            "radial-gradient(circle at center, transparent 45%, rgba(0,0,0,.55) 100%)",
                    }}
                />

                {/* Graph Links */}
                <svg
                    className="absolute inset-0 h-full w-full"
                    viewBox="0 0 100 100"
                    preserveAspectRatio="none"
                    style={{
                        filter:
                            "drop-shadow(0 0 8px rgba(139,92,246,.25))",
                    }}
                >
                    <defs>
                        <linearGradient
                            id="linkGradient"
                            x1="0"
                            y1="0"
                            x2="1"
                            y2="1"
                        >
                            <stop
                                offset="0%"
                                stopColor="#8b5cf6"
                                stopOpacity="0.1"
                            />
                            <stop
                                offset="50%"
                                stopColor="#a78bfa"
                                stopOpacity="0.5"
                            />
                            <stop
                                offset="100%"
                                stopColor="#ef4444"
                                stopOpacity="0.2"
                            />
                        </linearGradient>

                        <filter id="softGlow">
                            <feGaussianBlur
                                stdDeviation="2.5"
                                result="blur"
                            />
                            <feMerge>
                                <feMergeNode in="blur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>

                        <marker
                            id="arrow"
                            markerWidth="8"
                            markerHeight="8"
                            refX="7"
                            refY="4"
                            orient="auto"
                            markerUnits="strokeWidth"
                        >
                            <path
                                d="M0,0 L8,4 L0,8 Z"
                                fill="#a78bfa"
                                opacity="0.7"
                            />
                        </marker>
                    </defs>

                    {links.map(([a, b], i) => {
                        const start = nodes[a];
                        const end = nodes[b];

                        const dx = end.x - start.x;

                        const mx = (start.x + end.x) / 2;
                        const my =
                            (start.y + end.y) / 2 -
                            Math.abs(dx) * 0.18;

                        const path = `
                            M ${start.x} ${start.y}
                            Q ${mx} ${my}
                            ${end.x} ${end.y}
                        `;

                        return (
                            <g key={i}>
                                <path
                                    d={path}
                                    fill="none"
                                    stroke="rgba(139,92,246,0.08)"
                                    strokeWidth="1.4"
                                />

                                <path
                                    d={path}
                                    fill="none"
                                    stroke="url(#linkGradient)"
                                    strokeWidth="0.35"
                                    strokeLinecap="round"
                                    filter="url(#softGlow)"
                                    markerEnd="url(#arrow)"
                                />

                                <path
                                    d={path}
                                    fill="none"
                                    stroke="rgba(167,139,250,0.85)"
                                    strokeWidth="0.2"
                                    strokeDasharray="1 2"
                                    strokeLinecap="round"
                                >
                                    <animate
                                        attributeName="stroke-dashoffset"
                                        from="0"
                                        to="-20"
                                        dur="6s"
                                        repeatCount="indefinite"
                                    />
                                </path>
                            </g>
                        );
                    })}
                </svg>

                {/* Nodes */}
                {nodes.map((node) => (
                    <div
                        key={node.label}
                        className="
                            absolute
                            flex
                            h-28
                            w-28
                            -translate-x-1/2
                            -translate-y-1/2
                            flex-col
                            items-center
                            justify-center
                            rounded-full
                            border
                            border-white/10
                            bg-[#15192b]/90
                            text-center
                            backdrop-blur-xl
                            transition-all
                            duration-300
                            hover:scale-110
                            hover:-translate-y-[55%]
                            hover:shadow-[0_0_50px_rgba(139,92,246,.45)]
                        "
                        style={{
                            left: `${node.x}%`,
                            top: `${node.y}%`,
                            boxShadow: `
                                0 0 40px ${node.glow}30,
                                0 0 80px ${node.glow}15
                            `,
                        }}
                    >
                        <div
                            className="absolute inset-0 rounded-full"
                            style={{
                                border: `3px solid ${node.glow}`,
                                opacity: 0.8,
                            }}
                        />

                        <div className="text-[15px] font-medium text-white">
                            {node.label}
                        </div>

                        <div className="mt-1 text-sm text-zinc-400">
                            {node.percent}%
                        </div>
                    </div>
                ))}

                {/* Legend */}
                <div className="absolute bottom-4 left-4 flex items-center gap-4 rounded-xl border border-white/10 bg-black/30 px-4 py-2 text-sm text-zinc-300 backdrop-blur-md">
                    <div className="flex items-center gap-2">
                        <span className="text-cyan-500">●</span>
                        <span>CS</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="text-violet-500">●</span>
                        <span>Math</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="text-teal-500">●</span>
                        <span>Physics</span>
                    </div>
                </div>
            </div>
        </div>
    );
}