# Quick Setup Guide - Dynamic Profile Page

## 🚀 Quick Start (5 minutes)

Follow these steps to get the dynamic profile page working:

### Step 1: Run Database Migrations

1. Open your **Supabase Dashboard**
2. Go to **SQL Editor** → **New Query**
3. Copy and paste each file below, **one at a time**, and click **Run**:

#### Migration 1: User Profiles
Copy from: `backend/migrations/create_user_profiles_table.sql`

#### Migration 2: User Stats
Copy from: `backend/migrations/create_user_stats_table.sql`

#### Migration 3: Achievements
Copy from: `backend/migrations/create_user_achievements_table.sql`

### Step 2: Create Storage Bucket

1. In Supabase, go to **Storage**
2. Click **New Bucket**
3. Name: `profile-images`
4. Make it **Public**
5. Click **Create**

### Step 3: Set Storage Policies

In the SQL Editor, run this:

```sql
-- Allow users to upload their own avatar
CREATE POLICY "Users can upload their own avatar"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'profile-images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow users to update their own avatar
CREATE POLICY "Users can update their own avatar"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'profile-images' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow anyone to view avatars
CREATE POLICY "Anyone can view avatars"
ON storage.objects FOR SELECT
USING (bucket_id = 'profile-images');
```

### Step 4: Test It!

1. Start your backend: `cd backend && uvicorn app.main:app --reload`
2. Start your frontend: `cd frontend && npm run dev`
3. Login to your app
4. Navigate to the Profile page
5. Try editing your profile, uploading an avatar, and adding subjects!

## ✅ Verification

After setup, you should see:

- **3 new tables** in Supabase: `user_profiles`, `user_stats`, `user_achievements`
- **1 storage bucket**: `profile-images`
- **Profile page loads** with your user data
- **Edit mode works** - changes save to database
- **Avatar upload works** - images save to storage

## 🐛 Troubleshooting

### Profile doesn't load
- Check that all 3 migrations ran successfully
- Verify RLS policies are enabled
- Check browser console for errors

### Avatar upload fails
- Ensure `profile-images` bucket exists
- Verify bucket is set to **Public**
- Check storage policies are created

### Stats show as 0
- This is normal for new users
- Stats will update as you use the app
- You can manually update via SQL if needed for testing

## 📝 What's Next?

The profile page is now functional! To make it even better:

1. **Integrate stats tracking** - Call the stats increment endpoints when users:
   - Complete lessons
   - Chat with AI
   - Finish courses

2. **Achievement unlocking** - Add logic to check and unlock achievements based on user actions

3. **Profile completion** - Add a progress indicator showing profile completion percentage

## 🔗 Useful Links

- [Supabase Dashboard](https://app.supabase.com)
- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Supabase RLS Docs](https://supabase.com/docs/guides/auth/row-level-security)
