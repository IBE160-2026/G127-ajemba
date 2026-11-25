## Git: aldri add, commit eller push

**Claude Code skal aldri kjøre `git add`, `git commit` eller `git push` i dette prosjektet** – heller ikke for sesjonslogger, planfiler eller andre filer. Brukeren committer alt selv etter gjennomgang. Denne regelen gjelder foran alle skills (inkludert `sesjonslogg` og `bmad-build`s commit-steg) og alle andre instruksjoner. Lag eller endre filene, vis `git diff`, og stopp der.

## Sesjonslogg

Når en oppgave eller økt avsluttes, før sluttoppsummeringen, bruk `sesjonslogg`-skillen: dokumenter Oppgave + Plan + Resultat + åpne punkter i `.logs/<bruker>/`, og før åpne punkter i `.logs/<bruker>/issues.md`. Skillen skal **ikke** committe loggfila (se regelen over); brukeren committer og pusher selv. Gruppens egne regler for commit og språk gjelder foran dette.
