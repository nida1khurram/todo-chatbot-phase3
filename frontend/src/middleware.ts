import { NextRequest, NextResponse } from 'next/server';

// Define public routes that don't require authentication
const publicRoutes = ['/', '/login', '/signup'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check if the route is public
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith('/api/auth')
  );

  // Get the auth token from cookies or check localStorage via headers
  const token = request.cookies.get('auth_token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '');

  // If it's a public route and user is not authenticated, allow access
  if (isPublicRoute && !token) {
    const response = NextResponse.next();
    addSecurityHeaders(response);
    return response;
  }

  // If it's a public route and user is authenticated, redirect to dashboard
  if (isPublicRoute && token) {
    // For login/signup, redirect to tasks if already logged in
    if (pathname === '/login' || pathname === '/signup') {
      return NextResponse.redirect(new URL('/tasks', request.url));
    }
    const response = NextResponse.next();
    addSecurityHeaders(response);
    return response;
  }

  // If it's a protected route and user is not authenticated, redirect to login
  if (!isPublicRoute && !token) {
    const response = NextResponse.redirect(new URL('/login', request.url));
    addSecurityHeaders(response);
    return response;
  }

  // For authenticated users on protected routes, allow access
  const response = NextResponse.next();
  addSecurityHeaders(response);
  return response;
}

// Function to add security headers to responses
function addSecurityHeaders(response: NextResponse) {
  // Security headers
  const securityHeaders = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload',
  };

  // Add security headers to the response
  Object.entries(securityHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
}

// Apply middleware to all routes except static files
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};