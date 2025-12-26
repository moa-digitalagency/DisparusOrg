import { QueryClient, QueryFunction } from "@tanstack/react-query";

async function throwIfResNotOk(res: Response) {
  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }
}

export async function apiRequest(
  method: string,
  url: string,
  data?: unknown | undefined,
): Promise<Response> {
  const res = await fetch(url, {
    method,
    headers: data ? { "Content-Type": "application/json" } : {},
    body: data ? JSON.stringify(data) : undefined,
    credentials: "include",
  });

  await throwIfResNotOk(res);
  return res;
}

type UnauthorizedBehavior = "returnNull" | "throw";

export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
  ({ on401: unauthorizedBehavior }) =>
  async ({ queryKey }) => {
    // Handle query keys properly:
    // - If first element is a string starting with '/', use it as the base URL
    // - If there are additional elements that are objects, convert them to query params
    const baseUrl = queryKey[0] as string;
    
    let url = baseUrl;
    
    // If there's a second element that's an object, treat it as query params
    if (queryKey.length > 1 && typeof queryKey[1] === "object" && queryKey[1] !== null) {
      const params = queryKey[1] as Record<string, unknown>;
      const searchParams = new URLSearchParams();
      
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== "" && value !== "all") {
          searchParams.set(key, String(value));
        }
      }
      
      const qs = searchParams.toString();
      if (qs) {
        url = `${baseUrl}?${qs}`;
      }
    }
    
    const res = await fetch(url, {
      credentials: "include",
    });

    if (unauthorizedBehavior === "returnNull" && res.status === 401) {
      return null;
    }

    await throwIfResNotOk(res);
    return await res.json();
  };

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});
