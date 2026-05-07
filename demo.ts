import { fetchUserWithTasksREST, fetchUserWithTasksGraphQL } from "./client.js";

(async () => {
  const userId = "a14e06f4-62e2-47fd-a534-074ed8968328";
  
  console.log("REST:", await fetchUserWithTasksREST(userId));
  console.log("GraphQL:", await fetchUserWithTasksGraphQL(userId));
})();