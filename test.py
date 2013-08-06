#!/usr/bin/env python

import types
import Spacman as spac
from unittest import TestCase


class SpacmanTest(TestCase):
    def test_get_urls(self):
        urls = list(spac.get_urls('-S', ['linux',  'gvim']))
        self.assertEqual(2, len(urls))
        self.assertIsInstance(urls, list)

    def test_get_mirrors(self):
        mirrors = spac.get_mirrors()
        self.assertIsInstance(mirrors, types.GeneratorType)
        self.assertTrue(any(mirrors))

    def test_get_downloadurls(self):
        url = next(spac.get_urls('-S', ['gvim']))
        mirrors = spac.get_mirrors()

        urls = [x for x in spac.get_downloadurls(url, mirrors)]
        self.assertTrue(len(urls) >= 1)
