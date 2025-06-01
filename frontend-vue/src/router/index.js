import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ProfileView from '../views/ProfileView.vue'
import SuccessView from '../views/SuccessView.vue'
import { CONFIG } from '../constants'
import { BASE_URL } from '../constants'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
    {
      path: '/success',
      name: 'success',
      component: SuccessView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    // Admin routes
    {
      path: '/admin',
      component: () => import('../views/admin/DashboardLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'admin-dashboard',
          component: () => import('../views/admin/Dashboard.vue'),
        },
        {
          path: 'download',
          name: 'admin-download',
          component: () => import('../views/admin/Download.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/Users.vue')
        },
        {
          path: 'products',
          name: 'admin-products',
          component: () => import('../views/admin/Products.vue')
        },
        {
          path: 'contributions',
          name: 'admin-contributions',
          component: () => import('../views/admin/Contributions.vue')
        },
        {
          path: 'caption-history',
          name: 'admin-caption-history',
          component: () => import('../views/admin/CaptionHistory.vue')
        }
      ]
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('../views/admin/Login.vue')
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFound.vue')
    }
  ],
})

// Navigation guard to check authentication for admin routes
router.beforeEach((to, from, next) => {
  // Check if the route requires authentication and admin privileges
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Check both possible token locations (main site uses 'token', admin site uses CONFIG.TOKEN_KEY)
    const adminToken = localStorage.getItem(CONFIG.TOKEN_KEY);
    const mainToken = localStorage.getItem('token');
    const token = adminToken || mainToken;
    
    let user = null;
    try {
      const userString = localStorage.getItem('user');
      // Chỉ parse khi userString có dữ liệu
      if (userString) {
        user = JSON.parse(userString);
      } else {
        user = {};
      }
    } catch (e) {
      console.error("Error parsing user from localStorage:", e);
      user = {};
      // Xóa dữ liệu không hợp lệ
      localStorage.removeItem('user');
    }
    
    // If no token, redirect to login
    if (!token) {
      console.log('No token found, redirecting to admin login');
      next({
        path: '/admin/login',
        query: { reason: 'unauthorized', redirect: to.fullPath }
      });
      return;
    } 
    // If route requires admin but user is not admin
    else if (to.matched.some(record => record.meta.requiresAdmin) && 
             !(user.is_admin === true || user.isAdmin === true)) {
      console.log('User is not admin, redirecting to home page');
      // Redirect to home page (main site) if not admin
      window.location.href = BASE_URL;
      return;
    }
    else {
      // If we have a main token but no admin token, set the admin token
      if (mainToken && !adminToken && (user.is_admin === true || user.isAdmin === true)) {
        console.log('Setting main token as admin token');
        localStorage.setItem(CONFIG.TOKEN_KEY, mainToken);
      }
      
      // Continue to the route
      next();
    }
  } else {
    // If the route doesn't require authentication, proceed
    next();
  }
});

export default router
