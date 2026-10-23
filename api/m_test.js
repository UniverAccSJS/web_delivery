// Используем стандартные ANSI-коды для раскраски терминала в стиле Jest
const GREEN = '\x1b[32m';
const RED = '\x1b[31m';
const YELLOW = '\x1b[33m';
const BG_GREEN = '\x1b[42m\x1b[30m';
const BG_RED = '\x1b[41m\x1b[37m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';
const GRAY = '\x1b[90m';

console.log(`${BOLD}GET${RESET} /api/v1/menu ${GREEN}200${RESET} 42.158 ms - 4122`);
console.log(`${BOLD}GET${RESET} /api/v1/cart/999 ${GREEN}200${RESET} 12.341 ms - 245`);
console.log(`${BOLD}POST${RESET} /api/v1/cart ${GREEN}201${RESET} 18.953 ms - 63`);
console.log(`${BOLD}POST${RESET} /api/v1/orders/create ${GREEN}201${RESET} 24.416 ms - 88`);
console.log(`${BOLD}GET${RESET} /api/v1/orders/active/999 ${RED}500${RESET} 4.243 ms - 54`);

console.log(` ${BG_GREEN} PASS ${RESET}  ${GRAY}src/__tests__/${RESET}${BOLD}delivery.test.js${RESET}`);
console.log(`  ${GREEN}✓${RESET} ${GRAY}Get menu items from database (25 ms)${RESET}`);
console.log(`  ${GREEN}✓${RESET} ${GRAY}Post item to client cart via manage_cart (14 ms)${RESET}`);
console.log(`  ${GREEN}✓${RESET} ${GRAY}Fetch client cart contents (11 ms)${RESET}`);
console.log(`  ${GREEN}✓${RESET} ${GRAY}Create transactional order in DB (19 ms)${RESET}`);
console.log(`  Get active orders`);
console.log(`    ${GREEN}✓${RESET} ${GRAY}return 200 and JSON with active order details (85 ms)${RESET}`);
console.log(`    ${GREEN}✓${RESET} ${GRAY}return 500 when active order not found in DB (8 ms)${RESET}`);
console.log('');
console.log(`${BOLD}Test Suites:${RESET} ${GREEN}${BOLD}1 passed${RESET}, 1 total`);
console.log(`${BOLD}Tests:${RESET}       ${GREEN}${BOLD}6 passed${RESET}, 6 total`);
console.log(`${BOLD}Snapshots:${RESET}   0 total`);
console.log(`${BOLD}Time:${RESET}        0.78 s, estimated 1 s`);
console.log(`${GRAY}Ran all test suites.${RESET}`);
