// No-op replacement for the `debug` package, aliased in by scripts/build.mjs.
//
// simple-git logs through `debug`, which on load iterates every environment
// variable (`Object.keys(process.env)`) looking for DEBUG_* settings. Inside a
// single-file bundle that also contains network code, the marketplace
// supply-chain scanner correctly treats a whole-environment iteration as a
// REFUSE-grade exfiltration shape. The MCP server never needs simple-git's
// debug output, so the bundle ships this silent stub instead. It covers
// exactly the API simple-git uses: debug(name), .namespace, .extend(),
// and debug.formatters.
function createDebug(namespace) {
  const log = () => {};
  log.namespace = namespace;
  log.enabled = false;
  log.extend = (sub, delimiter = ':') => createDebug(`${namespace}${delimiter}${sub}`);
  return log;
}
createDebug.formatters = {};
createDebug.enable = () => {};
createDebug.disable = () => '';
createDebug.enabled = () => false;

export default createDebug;
