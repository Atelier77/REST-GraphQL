// types.ts
console.log("🟢 СКРИПТ ЗАПУЩЕН");
export interface User { id: string; name: string; email: string }
export interface Task { id: string; title: string; description: string; user_id: string }

// REST клиент (2 запроса)
export async function fetchUserWithTasksREST(userId: string): Promise<{ user: User; tasks: Task[] }> {
  // 1️⃣ Запрос пользователя
  const userRes = await fetch(`http://localhost:8000/users/${userId}`);
  if (!userRes.ok) throw new Error("User not found");
  const user: User = await userRes.json();

  // 2️⃣ Запрос всех задач и фильтрация на клиенте
  const tasksRes = await fetch(`http://localhost:8000/tasks`);
  const allTasks: Task[] = await tasksRes.json();
  const userTasks = allTasks.filter(t => t.user_id === userId);

  return { user, tasks: userTasks };
}

// GraphQL клиент (1 запрос)
export async function fetchUserWithTasksGraphQL(userId: string): Promise<{ user: User; tasks: Task[] }> {
  const query = `
    query GetUserWithTasks($id: ID!) {
      user(id: $id) {
        id
        name
        email
        tasks {
          id
          title
          description
        }
      }
    }
  `;

  const res = await fetch("http://localhost:8000/graphql", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables: { id: userId } }),
  });

  const json = await res.json();
  if (json.errors) throw new Error(json.errors[0].message);
  return json.data.user;
}