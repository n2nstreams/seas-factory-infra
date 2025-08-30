-- Supabase Storage Setup for Module 4: File/Object Storage
-- This script creates storage buckets and policies for the SaaS Factory platform
-- Run this in your Supabase SQL editor to set up the storage foundation

-- Enable storage extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "storage";

-- Create storage buckets
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
  ('user-uploads', 'user-uploads', false, 10485760, ARRAY['image/*', 'application/pdf', 'text/*', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']),
  ('project-assets', 'project-assets', false, 52428800, ARRAY['image/*', 'application/pdf', 'text/*', 'application/zip', 'application/x-zip-compressed']),
  ('temp-files', 'temp-files', false, 10485760, ARRAY['*/*']),
  ('public-assets', 'public-assets', true, 10485760, ARRAY['image/*', 'text/css', 'application/javascript'])
ON CONFLICT (id) DO NOTHING;

-- Create storage objects table for tracking uploaded files
CREATE TABLE IF NOT EXISTS storage_objects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  bucket_id TEXT NOT NULL REFERENCES storage.buckets(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  owner UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  
  -- File metadata
  size BIGINT NOT NULL,
  mime_type TEXT,
  metadata JSONB DEFAULT '{}',
  
  -- Storage path
  storage_path TEXT NOT NULL,
  public_url TEXT,
  
  -- Audit fields
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(bucket_id, name)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_storage_objects_tenant_id ON storage_objects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_storage_objects_owner ON storage_objects(owner);
CREATE INDEX IF NOT EXISTS idx_storage_objects_bucket_path ON storage_objects(bucket_id, storage_path);
CREATE INDEX IF NOT EXISTS idx_storage_objects_created_at ON storage_objects(created_at);

-- Enable Row Level Security
ALTER TABLE storage_objects ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for storage objects
-- Policy: Users can view objects in their tenant
CREATE POLICY "Users can view objects in their tenant" ON storage_objects
  FOR SELECT USING (
    tenant_id IN (
      SELECT tenant_id FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can insert objects in their tenant
CREATE POLICY "Users can insert objects in their tenant" ON storage_objects
  FOR INSERT WITH CHECK (
    tenant_id IN (
      SELECT tenant_id FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can update objects they own in their tenant
CREATE POLICY "Users can update objects they own in their tenant" ON storage_objects
  FOR UPDATE USING (
    owner = auth.uid() AND
    tenant_id IN (
      SELECT tenant_id FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can delete objects they own in their tenant
CREATE POLICY "Users can delete objects they own in their tenant" ON storage_objects
  FOR DELETE USING (
    owner = auth.uid() AND
    tenant_id IN (
      SELECT tenant_id FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Public assets are viewable by everyone
CREATE POLICY "Public assets are viewable by everyone" ON storage_objects
  FOR SELECT USING (
    bucket_id = 'public-assets'
  );

-- Create storage policies for buckets
-- Policy: Users can upload to user-uploads bucket in their tenant
CREATE POLICY "Users can upload to user-uploads in their tenant" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'user-uploads' AND
    (storage.foldername(name))[1] IN (
      SELECT tenant_id::text FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can view objects in user-uploads bucket in their tenant
CREATE POLICY "Users can view user-uploads in their tenant" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'user-uploads' AND
    (storage.foldername(name))[1] IN (
      SELECT tenant_id::text FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can upload to project-assets bucket in their tenant
CREATE POLICY "Users can upload to project-assets in their tenant" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'project-assets' AND
    (storage.foldername(name))[1] IN (
      SELECT tenant_id::text FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can view objects in project-assets bucket in their tenant
CREATE POLICY "Users can view project-assets in their tenant" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'project-assets' AND
    (storage.foldername(name))[1] IN (
      SELECT tenant_id::text FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can upload to temp-files bucket in their tenant
CREATE POLICY "Users can upload to temp-files in their tenant" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'temp-files' AND
    (storage.foldername(name))[1] IN (
      SELECT tenant_id::text FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Users can view temp-files in their tenant
CREATE POLICY "Users can view temp-files in their tenant" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'temp-files' AND
    (storage.foldername(name))[1] IN (
      SELECT tenant_id::text FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Policy: Public assets are viewable by everyone
CREATE POLICY "Public assets are viewable by everyone" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'public-assets'
  );

-- Policy: Authenticated users can upload to public-assets
CREATE POLICY "Authenticated users can upload to public-assets" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'public-assets' AND
    auth.role() = 'authenticated'
  );

-- Create function to automatically create storage object record
CREATE OR REPLACE FUNCTION handle_storage_object_created()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO storage_objects (
    bucket_id,
    name,
    owner,
    tenant_id,
    size,
    mime_type,
    metadata,
    storage_path,
    public_url
  ) VALUES (
    NEW.bucket_id,
    NEW.name,
    NEW.owner,
    (storage.foldername(NEW.name))[1]::UUID,
    NEW.metadata->>'size',
    NEW.metadata->>'mimetype',
    NEW.metadata,
    NEW.name,
    storage.get_public_url(NEW.bucket_id, NEW.name)
  );
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically create storage object record
DROP TRIGGER IF EXISTS on_storage_object_created ON storage.objects;
CREATE TRIGGER on_storage_object_created
  AFTER INSERT ON storage.objects
  FOR EACH ROW EXECUTE FUNCTION handle_storage_object_created();

-- Create function to update storage object record
CREATE OR REPLACE FUNCTION handle_storage_object_updated()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE storage_objects SET
    size = COALESCE(NEW.metadata->>'size', size),
    mime_type = COALESCE(NEW.metadata->>'mimetype', mime_type),
    metadata = NEW.metadata,
    updated_at = NOW()
  WHERE bucket_id = NEW.bucket_id AND name = NEW.name;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically update storage object record
DROP TRIGGER IF EXISTS on_storage_object_updated ON storage.objects;
CREATE TRIGGER on_storage_object_updated
  AFTER UPDATE ON storage.objects
  FOR EACH ROW EXECUTE FUNCTION handle_storage_object_updated();

-- Create function to delete storage object record
CREATE OR REPLACE FUNCTION handle_storage_object_deleted()
RETURNS TRIGGER AS $$
BEGIN
  DELETE FROM storage_objects 
  WHERE bucket_id = OLD.bucket_id AND name = OLD.name;
  
  RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically delete storage object record
DROP TRIGGER IF EXISTS on_storage_object_deleted ON storage.objects;
CREATE TRIGGER on_storage_object_deleted
  AFTER DELETE ON storage.objects
  FOR EACH ROW EXECUTE FUNCTION handle_storage_object_deleted();

-- Create function to get storage usage by tenant
CREATE OR REPLACE FUNCTION get_tenant_storage_usage(tenant_uuid UUID)
RETURNS TABLE(
  bucket_id TEXT,
  total_files BIGINT,
  total_size BIGINT,
  total_size_mb NUMERIC
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    so.bucket_id,
    COUNT(*) as total_files,
    COALESCE(SUM(so.size), 0) as total_size,
    ROUND(COALESCE(SUM(so.size), 0) / 1024.0 / 1024.0, 2) as total_size_mb
  FROM storage_objects so
  WHERE so.tenant_id = tenant_uuid
  GROUP BY so.bucket_id
  ORDER BY so.bucket_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA storage TO authenticated;
GRANT ALL ON storage.objects TO authenticated;
GRANT ALL ON storage.buckets TO authenticated;

-- Create storage migration tracking table
CREATE TABLE IF NOT EXISTS storage_migration_status (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  bucket_id TEXT NOT NULL,
  migration_stage TEXT NOT NULL CHECK (migration_stage IN ('pending', 'in_progress', 'completed', 'failed')),
  objects_migrated INTEGER DEFAULT 0,
  total_objects INTEGER DEFAULT 0,
  last_migration_at TIMESTAMP WITH TIME ZONE,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(tenant_id, bucket_id)
);

-- Create index for migration status
CREATE INDEX IF NOT EXISTS idx_storage_migration_status_tenant ON storage_migration_status(tenant_id);
CREATE INDEX IF NOT EXISTS idx_storage_migration_status_stage ON storage_migration_status(migration_stage);

-- Enable RLS on migration status table
ALTER TABLE storage_migration_status ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view migration status for their tenant
CREATE POLICY "Users can view migration status for their tenant" ON storage_migration_status
  FOR SELECT USING (
    tenant_id IN (
      SELECT tenant_id FROM user_tenants 
      WHERE user_id = auth.uid() AND status = 'active'
    )
  );

-- Insert default migration status for existing tenants
INSERT INTO storage_migration_status (tenant_id, bucket_id, migration_stage, total_objects)
SELECT 
  t.id,
  b.id,
  'pending',
  0
FROM tenants t
CROSS JOIN storage.buckets b
WHERE NOT EXISTS (
  SELECT 1 FROM storage_migration_status sms 
  WHERE sms.tenant_id = t.id AND sms.bucket_id = b.id
);

-- Output setup completion message
SELECT 'Supabase Storage setup completed successfully!' as status;
