# Czech and Slovak Pi-hole blocklist

A conservative DNS-level conversion of
[EasyList Czech and Slovak](https://github.com/tomasko126/easylistczechandslovak)
for current Pi-hole releases.

The generated list keeps only unmodified domain-wide rules in the form
`||example.cz^`. Cosmetic filters, URL/path rules, exception rules, resource
types, `$domain` restrictions and `$third-party` rules are discarded because
their browser context cannot be represented safely at DNS level.

## Pi-hole setup

Add these URLs under **Settings -> Lists** and update gravity:

```text
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/pro.txt
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/adblock/tif.mini.txt
https://raw.githubusercontent.com/vojthor/pihole-czsk-blocklist/main/easylist-czsk-pihole.txt
```

The first URL is the main ads/tracking list, the second adds malware and
phishing coverage, and the third contributes Czech and Slovak domains that can
be converted safely from the regional browser list.

Avoid stacking OISD, StevenBlack or AdGuard DNS Filter with these: their useful
coverage overlaps heavily with HaGeZi Pro.

## Automatic updates

GitHub Actions runs the converter daily. It resolves upstream `!#include`
directives, validates domains, deduplicates the result and commits only when the
generated list changes.

The converter tests also run on every push and pull request, with read-only
repository permissions and without downloading the upstream list.

GitHub can disable scheduled workflows in public repositories after 60 days of
inactivity, even when the daily conversion finds no changes. If updates stop,
open **Actions -> Update blocklist**, enable the workflow if needed, then select
**Run workflow** to refresh the list. See
[GitHub's workflow documentation](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/disabling-and-enabling-a-workflow)
for details.

Run it locally with:

```bash
python -m unittest discover -s tests -v
python scripts/build_czsk_dns.py
```

## License and attribution

The generated blocklist is adapted from EasyList Czech and Slovak, maintained
by its contributors and licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The generated
list is distributed under the same license. Changes consist of selecting only
DNS-safe rules, normalizing domain names, sorting and deduplicating them.
