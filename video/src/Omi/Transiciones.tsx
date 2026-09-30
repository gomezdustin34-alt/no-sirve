import React from "react";
import { AbsoluteFill, Easing } from "remotion";
import type {
  TransitionPresentation,
  TransitionPresentationComponentProps,
} from "@remotion/transitions";

type SinProps = Record<string, never>;

/** Zoom a través: el plano que sale se acerca y se desenfoca; el nuevo aparece enfocándose. */
const Zoom: React.FC<TransitionPresentationComponentProps<SinProps>> = ({
  children,
  presentationDirection,
  presentationProgress,
}) => {
  const p = Easing.inOut(Easing.cubic)(presentationProgress);
  const estilo: React.CSSProperties =
    presentationDirection === "exiting"
      ? {
          transform: `scale(${1 + p * 1.4})`,
          filter: `blur(${p * 22}px) brightness(${1 + p * 0.6})`,
          opacity: 1 - Math.max(0, p - 0.5) * 2,
        }
      : {
          transform: `scale(${0.75 + p * 0.25})`,
          filter: `blur(${(1 - p) * 22}px) brightness(${1 + (1 - p) * 0.6})`,
          opacity: Math.min(1, p * 2),
        };
  return <AbsoluteFill style={estilo}>{children}</AbsoluteFill>;
};

/** Latigazo: paneo muy rápido con desenfoque de movimiento. */
const Latigazo: React.FC<TransitionPresentationComponentProps<SinProps>> = ({
  children,
  presentationDirection,
  presentationProgress,
}) => {
  const p = Easing.inOut(Easing.quad)(presentationProgress);
  const blur = Math.sin(Math.PI * p) * 28;
  const x = presentationDirection === "exiting" ? -p * 100 : (1 - p) * 100;
  return (
    <AbsoluteFill
      style={{
        transform: `translateX(${x}%) skewX(${Math.sin(Math.PI * p) * -8}deg)`,
        filter: `blur(${blur}px)`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

export const zoomTraves = (): TransitionPresentation<SinProps> => ({
  component: Zoom,
  props: {},
});

export const latigazo = (): TransitionPresentation<SinProps> => ({
  component: Latigazo,
  props: {},
});
