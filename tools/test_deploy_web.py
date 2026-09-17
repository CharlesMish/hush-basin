"""Tests for the promotion barriers; no Cloudflare mutations."""
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

import deploy_web as lane


class PromotionBarriers(unittest.TestCase):
    def candidate(self, work):
        candidate = {'http_verified': True, 'inventory': {'site/index.html': 'original'},
                     'previous': {'current_build_id': 'old'}}
        (work / 'candidate.json').write_text(json.dumps(candidate))
        return candidate

    def test_requires_explicit_playable_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(lane, 'deploy') as deploy:
            work = Path(tmp)
            self.candidate(work)
            with self.assertRaisesRegex(RuntimeError, 'Play the exact preview'):
                lane.promote(types.SimpleNamespace(work=work, confirm_playable=False))
            deploy.assert_not_called()

    def test_changed_candidate_cannot_promote(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(lane, 'deploy') as deploy:
            work = Path(tmp)
            self.candidate(work)
            with patch.object(lane, 'inventory', return_value={'site/index.html': 'changed'}):
                with self.assertRaisesRegex(RuntimeError, 'Candidate files changed'):
                    lane.promote(types.SimpleNamespace(work=work, confirm_playable=True))
            deploy.assert_not_called()

    def test_stale_preview_cannot_remove_newer_production_builds(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(lane, 'deploy') as deploy:
            work = Path(tmp)
            candidate = self.candidate(work)
            with patch.object(lane, 'inventory', return_value=candidate['inventory']), \
                 patch.object(lane, 'current_release', return_value={'current_build_id': 'new'}):
                with self.assertRaisesRegex(RuntimeError, 'Production changed'):
                    lane.promote(types.SimpleNamespace(work=work, confirm_playable=True))
            deploy.assert_not_called()

    def test_missing_http_verification_cannot_promote(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(lane, 'deploy') as deploy:
            work = Path(tmp)
            candidate = self.candidate(work)
            candidate['http_verified'] = False
            (work / 'candidate.json').write_text(json.dumps(candidate))
            with self.assertRaisesRegex(RuntimeError, 'Preview HTTP verification missing'):
                lane.promote(types.SimpleNamespace(work=work, confirm_playable=True))
            deploy.assert_not_called()


if __name__ == '__main__':
    unittest.main()
