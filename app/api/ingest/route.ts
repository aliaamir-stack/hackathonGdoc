import { NextResponse } from "next/server";

/**
 * Development stub: echoes what was received. Replace with a proxy to your real API or remove when using NEXT_PUBLIC_INGEST_URL only.
 */
export async function POST(request: Request) {
  let hasImage = false;
  let hasAudio = false;
  let imageName: string | null = null;
  let audioName: string | null = null;

  try {
    const form = await request.formData();
    const image = form.get("image");
    const audio = form.get("audio");
    if (image instanceof File && image.size > 0) {
      hasImage = true;
      imageName = image.name;
    }
    if (audio instanceof File && audio.size > 0) {
      hasAudio = true;
      audioName = audio.name;
    }
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid multipart body" },
      { status: 400 }
    );
  }

  if (!hasImage && !hasAudio) {
    return NextResponse.json(
      { ok: false, error: "Provide at least an image or an audio recording." },
      { status: 400 }
    );
  }

  return NextResponse.json({
    ok: true,
    message: "Stub ingest — point NEXT_PUBLIC_INGEST_URL at your backend for real processing.",
    received: { hasImage, hasAudio, imageName, audioName },
  });
}
