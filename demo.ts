import { fetchUserWithTasksREST, fetchUserWithTasksGraphQL } from "./client.js";

(async () => {
  const userId = "4e88cf9b-c5f0-401c-9efd-0ce9734a93ae";
  
  console.log("🚀 REST:", await fetchUserWithTasksREST(userId));
  console.log("🍓 GraphQL:", await fetchUserWithTasksGraphQL(userId));
})();