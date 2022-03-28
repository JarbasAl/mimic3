# Copyright 2022 Mycroft AI Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
.PHONY: dist docker

dist:
	cd opentts-abc && python3 setup.py sdist
	cd mimic3-tts && python3 setup.py sdist
	cd mimic3-http && python3 setup.py sdist
	mkdir -p dist
	cp opentts-abc/dist/opentts_abc-*.tar.gz dist/
	cp mimic3-tts/dist/mimic3_tts-*.tar.gz dist/
	cp mimic3-http/dist/mimic3_http-*.tar.gz dist/

docker:
	docker buildx build . -f Dockerfile --tag mycroftai/mimic3 --load
