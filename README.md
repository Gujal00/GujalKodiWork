# Arsath Jabbar Kodi Add-ons

This repository is a personal Kodi add-on repository maintained by Arsath Jabbar. The included add-ons retain their original authorship and provider information.

## Install the repository in Kodi

1. Make sure this repository is published as a **public** GitHub repository at `https://github.com/arsathjabbar/AbdulKodiWork`, and that the `master` branch contains the latest files.
2. Download the repository installer ZIP: [repository.arsathjabbar-1.0.0.zip](https://raw.githubusercontent.com/arsathjabbar/AbdulKodiWork/master/zips/repository.arsathjabbar/repository.arsathjabbar-1.0.0.zip). Transfer the ZIP to your Kodi device if needed; do not unzip it.
3. In Kodi, open **Settings → System → Add-ons** and enable **Unknown sources**.
4. Go to **Add-ons → Add-on browser → Install from zip file**, select the downloaded ZIP, and confirm the warning.
5. Wait for Kodi to report that **Arsath Jabbar Kodi Add-ons** is installed. Open **Install from repository**, choose it, then select an add-on to install.

Kodi will retrieve the repository index, checksum, and add-on ZIPs from this GitHub repository. If you publish from a different GitHub account, repository name, or branch, update the URLs in both `repository.arsathjabbar/addon.xml` and `addons.xml`, rebuild the repository ZIP, and regenerate `addons.xml.md5` before installing.

## Included add-ons

| Name | Version | Package |
|---|---:|---|
| Radios India | 0.3.5 | `plugin.audio.radiosindia` |
| Deccan Delight | 2.0.61 | `plugin.video.deccandelight` |
| f4mTester | 2.7.1 | `plugin.video.f4mTester` |
| Live Streams Pro | 2.9.7 | `plugin.video.live.streamspro` |
| Subscene | 2.1.5 | `service.subtitles.subscene` |

Other add-ons and dependencies are listed in [`addons.xml`](addons.xml).

## Attribution and use

These add-ons and their developers are not affiliated with Kodi or the sites and providers used by the add-ons. The add-ons do not host, create, or distribute the content they display. Keep each add-on's original provider, license, copyright notices, and terms when redistributing it. The upstream repository states that its add-ons are free/open-source and may not be sold or redistributed for commercial purposes; follow those terms unless the relevant author or license says otherwise.
