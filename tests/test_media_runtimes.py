import unittest

from shared.avatar import AvatarRuntime, AvatarState
from shared.emotion import EmotionLabel, ModalityEmotionResult, fuse_emotions
from shared.voice_runtime import BoundedAudioBuffer, StubSTTAdapter, StubTTSAdapter, has_speech, timed_synthesize, timed_transcribe


class MediaRuntimeTests(unittest.TestCase):
    def test_avatar_replay_viseme_and_fallback(self) -> None:
        avatar = AvatarRuntime(slow_frame_ms=20)
        avatar.transition(AvatarState.LISTENING)
        avatar.record(avatar.map_viseme("aa", 0.8), "nod")
        avatar.observe_frame_time(30)

        self.assertEqual(avatar.replay()[0].blend_shapes, {"jawOpen": 0.8})
        self.assertTrue(avatar.low_performance)

    def test_emotion_fusion_ignores_missing_confidence(self) -> None:
        fused = fuse_emotions([
            ModalityEmotionResult("text", EmotionLabel.HAPPY, 0.9, 0.8),
            ModalityEmotionResult("voice", EmotionLabel.SAD, 0.2, 0.5),
            ModalityEmotionResult("gaze", EmotionLabel.ANXIOUS, 0.0, 0.7),
        ])

        self.assertEqual(fused.dominant, EmotionLabel.HAPPY)
        self.assertEqual(fused.modalities, ("text", "voice"))

    def test_voice_buffer_is_bounded_and_cancellable(self) -> None:
        buffer = BoundedAudioBuffer(max_chunks=2)
        for chunk in (b"one", b"two", b"three"):
            buffer.push(chunk)
        self.assertEqual(buffer.payload().data, b"twothree")
        self.assertTrue(has_speech(bytes([128, 150])))
        buffer.cancel()
        with self.assertRaises(RuntimeError):
            buffer.push(b"four")

    def test_ci_safe_voice_adapters_report_latency(self) -> None:
        transcript = timed_transcribe(StubSTTAdapter(), BoundedAudioBuffer().payload())
        speech = timed_synthesize(StubTTSAdapter(), "hello world")

        self.assertEqual(transcript.value.text, "audio received")
        self.assertEqual(speech.value.text, "hello world")
        self.assertGreaterEqual(speech.latency_ms, 0)

    def test_voice_pipeline_tracks_streaming_and_adapter_selection(self) -> None:
        from shared.voice_runtime import VoicePipeline, VoiceSession

        session = VoiceSession(
            stt_adapter=StubSTTAdapter(),
            tts_adapter=StubTTSAdapter(),
            max_buffer_ms=200,
        )
        session.push_audio(b"hello world")
        result = session.transcribe()
        self.assertEqual(result.text, "hello world")
        self.assertEqual(session.synthesize("hello world").text, "hello world")

        pipeline = VoicePipeline(StubSTTAdapter(), StubTTSAdapter())
        self.assertEqual(pipeline.run(b"hello world", "hello world").transcript.text, "hello world")

    def test_voice_stream_rejects_overflow_and_supports_http_round_trip(self) -> None:
        from shared.voice_runtime import VoiceSession

        session = VoiceSession(max_buffer_ms=10)
        session.push_audio(b"abc")
        session.cancel()
        with self.assertRaises(RuntimeError):
            session.push_audio(b"more")

        from services.voice.main import create_server

        self.assertIsNotNone(create_server(port=0))

    def test_avatar_scene_and_fallback_state_are_wired(self) -> None:
        from shared.avatar import AvatarScene, AvatarState

        runtime = AvatarRuntime(slow_frame_ms=20)
        scene = AvatarScene(
            scene_id="placeholder",
            asset_uri="assets/avatar.glb",
            fallback_state=AvatarState.FALLBACK,
            default_state=AvatarState.IDLE,
        )
        runtime.set_scene(scene)
        runtime.transition(AvatarState.LISTENING)
        runtime.transition(AvatarState.THINKING)
        runtime.transition(AvatarState.SPEAKING)
        runtime.transition(AvatarState.FALLBACK)

        self.assertEqual(runtime.scene.asset_uri, "assets/avatar.glb")
        self.assertEqual(runtime.state, AvatarState.FALLBACK)
        self.assertTrue(runtime.snapshot()["fallback"])


if __name__ == "__main__":
    unittest.main()