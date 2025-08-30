import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';

interface EventFilter {
  event_types?: string[];
  sources?: string[];
  priority?: string[];
  search?: string;
  time_range?: string;
}

interface EventFilterPanelProps {
  filters: EventFilter;
  onFiltersChange: (filters: EventFilter) => void;
  className?: string;
}

const EventFilterPanel: React.FC<EventFilterPanelProps> = ({
  filters,
  onFiltersChange,
  className = ""
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Available filter options
  const availableEventTypes = [
    'agent_request', 'agent_response', 'agent_error',
    'system_health', 'metrics', 'test', 'connection'
  ];
  
  const availableSources = [
    'requirements_agent', 'idea_agent', 'market_agent',
    'orchestrator', 'dashboard', 'system'
  ];
  
  const availablePriorities = ['high', 'normal', 'low'];
  
  const timeRanges = [
    { value: '5m', label: 'Last 5 minutes' },
    { value: '15m', label: 'Last 15 minutes' },
    { value: '1h', label: 'Last hour' },
    { value: '6h', label: 'Last 6 hours' },
    { value: '24h', label: 'Last 24 hours' }
  ];

  const handleFilterChange = (key: keyof EventFilter, value: any) => {
    const newFilters = { ...filters, [key]: value };
    onFiltersChange(newFilters);
  };

  const handleMultiSelectChange = (key: keyof EventFilter, option: string) => {
    const currentValues = filters[key] as string[] || [];
    const newValues = currentValues.includes(option)
      ? currentValues.filter(v => v !== option)
      : [...currentValues, option];
    
    handleFilterChange(key, newValues.length > 0 ? newValues : undefined);
  };

  const clearFilters = () => {
    onFiltersChange({});
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.event_types?.length) count++;
    if (filters.sources?.length) count++;
    if (filters.priority?.length) count++;
    if (filters.search) count++;
    if (filters.time_range) count++;
    return count;
  };

  const hasActiveFilters = getActiveFilterCount() > 0;

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-slate-800 flex items-center gap-2">
            Event Filters
            {hasActiveFilters && (
              <Badge className="bg-emerald-500/10 text-emerald-700 border-emerald-500/20">
                {getActiveFilterCount()} active
              </Badge>
            )}
          </CardTitle>
          
          <div className="flex items-center gap-2">
            {hasActiveFilters && (
              <Button
                onClick={clearFilters}
                variant="outline"
                size="sm"
                className="text-slate-600 border-slate-200"
              >
                Clear All
              </Button>
            )}
            
            <Button
              onClick={() => setIsExpanded(!isExpanded)}
              variant="outline"
              size="sm"
              className="text-slate-600 border-slate-200"
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Search Filter */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Search Events
          </label>
          <Input
            type="text"
            placeholder="Search by event type, source, or data content..."
            value={filters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value || undefined)}
            className="w-full"
          />
        </div>

        {/* Quick Time Range */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Time Range
          </label>
          <div className="flex flex-wrap gap-2">
            {timeRanges.map((range) => (
              <Button
                key={range.value}
                onClick={() => handleFilterChange('time_range', 
                  filters.time_range === range.value ? undefined : range.value
                )}
                variant={filters.time_range === range.value ? "default" : "outline"}
                size="sm"
                className={filters.time_range === range.value 
                  ? "bg-emerald-500/80 text-white" 
                  : "border-slate-200 text-slate-600"
                }
              >
                {range.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Expandable Advanced Filters */}
        {isExpanded && (
          <div className="space-y-4 pt-4 border-t border-slate-200/50">
            
            {/* Event Types Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Event Types
                {filters.event_types?.length && (
                  <span className="ml-2 text-xs text-slate-500">
                    ({filters.event_types.length} selected)
                  </span>
                )}
              </label>
              <div className="flex flex-wrap gap-2">
                {availableEventTypes.map((type) => (
                  <Button
                    key={type}
                    onClick={() => handleMultiSelectChange('event_types', type)}
                    variant={filters.event_types?.includes(type) ? "default" : "outline"}
                    size="sm"
                    className={filters.event_types?.includes(type)
                      ? "bg-blue-500/80 text-white"
                      : "border-slate-200 text-slate-600"
                    }
                  >
                    {type}
                  </Button>
                ))}
              </div>
            </div>

            {/* Sources Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Sources
                {filters.sources?.length && (
                  <span className="ml-2 text-xs text-slate-500">
                    ({filters.sources.length} selected)
                  </span>
                )}
              </label>
              <div className="flex flex-wrap gap-2">
                {availableSources.map((source) => (
                  <Button
                    key={source}
                    onClick={() => handleMultiSelectChange('sources', source)}
                    variant={filters.sources?.includes(source) ? "default" : "outline"}
                    size="sm"
                    className={filters.sources?.includes(source)
                      ? "bg-purple-500/80 text-white"
                      : "border-slate-200 text-slate-600"
                    }
                  >
                    {source}
                  </Button>
                ))}
              </div>
            </div>

            {/* Priority Filter */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Priority
                {filters.priority?.length && (
                  <span className="ml-2 text-xs text-slate-500">
                    ({filters.priority.length} selected)
                  </span>
                )}
              </label>
              <div className="flex flex-wrap gap-2">
                {availablePriorities.map((priority) => {
                  const isSelected = filters.priority?.includes(priority);
                  const colorClass = priority === 'high' ? 'bg-red-500/80' :
                                   priority === 'normal' ? 'bg-green-500/80' : 'bg-yellow-500/80';
                  
                  return (
                    <Button
                      key={priority}
                      onClick={() => handleMultiSelectChange('priority', priority)}
                      variant={isSelected ? "default" : "outline"}
                      size="sm"
                      className={isSelected
                        ? `${colorClass} text-white`
                        : "border-slate-200 text-slate-600"
                      }
                    >
                      {priority}
                    </Button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Active Filters Summary */}
        {hasActiveFilters && (
          <div className="mt-4 pt-4 border-t border-slate-200/50">
            <div className="text-sm text-slate-600 mb-2">Active Filters:</div>
            <div className="flex flex-wrap gap-2">
              {filters.search && (
                <Badge className="bg-slate-100 text-slate-700">
                  Search: "{filters.search}"
                </Badge>
              )}
              {filters.time_range && (
                <Badge className="bg-slate-100 text-slate-700">
                  Time: {timeRanges.find(r => r.value === filters.time_range)?.label}
                </Badge>
              )}
              {filters.event_types?.map(type => (
                <Badge key={type} className="bg-blue-100 text-blue-700">
                  Type: {type}
                </Badge>
              ))}
              {filters.sources?.map(source => (
                <Badge key={source} className="bg-purple-100 text-purple-700">
                  Source: {source}
                </Badge>
              ))}
              {filters.priority?.map(priority => (
                <Badge key={priority} className="bg-green-100 text-green-700">
                  Priority: {priority}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export { EventFilterPanel }; 