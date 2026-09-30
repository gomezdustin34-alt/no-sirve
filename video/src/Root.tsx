import "./index.css";
import { Composition } from "remotion";
import { Aftermovie } from "./Omi/Aftermovie";
import { VERTICAL } from "./Omi/config";
import { esquemaRevisar, Revisar } from "./Omi/Revisar";
import { FPS, TIMELINE } from "./Omi/timeline";

const ANCHO = VERTICAL ? 1080 : 1920;
const ALTO = VERTICAL ? 1920 : 1080;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* El aftermovie. Renderizar con: npx remotion render OMI out/omi.mp4 */}
      <Composition
        id="OMI"
        component={Aftermovie}
        durationInFrames={TIMELINE.total}
        fps={FPS}
        width={ANCHO}
        height={ALTO}
      />

      {/* Para mirar un clip crudo y anotar el segundo exacto ("desde"). */}
      <Composition
        id="Revisar"
        component={Revisar}
        schema={esquemaRevisar}
        durationInFrames={FPS * 60 * 5}
        fps={FPS}
        width={ANCHO}
        height={ALTO}
        defaultProps={{ archivo: "" }}
      />
    </>
  );
};
