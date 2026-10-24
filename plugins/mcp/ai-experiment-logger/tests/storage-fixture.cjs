const os = require('node:os');
const { syncBuiltinESMExports } = require('node:module');
if (!process.env.CCPI_TEST_STORAGE_ROOT) throw new Error('fixture storage root required');
// Mock storage only in the owned test child; HOME remains unchanged.
os.homedir = () => process.env.CCPI_TEST_STORAGE_ROOT;
syncBuiltinESMExports();
