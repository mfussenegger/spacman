#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
import Spacman as spac


class SpacmanTest(TestCase):
    def test_get_urls(self):
        urls = spac.get_urls('-S', ['linux',  'gvim'])
        self.assertEqual(2, len(urls))
        self.assertIsInstance(urls, list)

    def test_get_mirrors_mirrorlist(self):
        mirrors = spac.get_mirrors_mirrorlist()
        self.assertIsInstance(mirrors, list)
        self.assertTrue(len(mirrors) >= 1)

    def test_get_downloadurls(self):
        url = spac.get_urls('-S', ['gvim'])[0]
        mirrors = spac.get_mirrors_mirrorlist()

        urls = [x for x in spac.get_downloadurls(url, mirrors)]
        self.assertTrue(len(urls) >= 1)
