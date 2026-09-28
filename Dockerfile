# The Casebook, served by nginx inside the cluster. See deploy/README.md.
#
# The build runs tools/check-dist.mjs, so an image cannot contain a page with an
# inline script, a script from another host, or a storage key the Casebook does
# not own: the pages are served on the same origin as the platform's console.

FROM node:22-alpine AS build

ENV ASTRO_TELEMETRY_DISABLED=1
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /repo

RUN corepack enable

COPY site/package.json site/pnpm-lock.yaml site/
RUN cd site && pnpm install --frozen-lockfile

COPY . .
RUN cd site && rm -rf dist && pnpm build \
    && cd .. && node tools/check-dist.mjs site/dist


FROM nginx:1.27-alpine AS runtime

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/site/dist /usr/share/nginx/html/casebook

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
